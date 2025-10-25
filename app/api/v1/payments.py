from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.payment import (
    PaymentRequest, PaymentResponse, PaymentStatus, 
    PaymentCalculationResponse, ProductItemRequest
)
from app.services.payment_service import PaymentService
from app.services.monobank_service import MonobankService
from app.services.product_service import ProductService
from app.repositories.payment_repository import PaymentRepository
from app.repositories.product_repository import ProductRepository
from app.database import get_db
from typing import Dict, Any, List

router = APIRouter(prefix="/payments", tags=["payments"])


def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    """Dependency для отримання сервісу товарів"""
    product_repository = ProductRepository(db)
    return ProductService(product_repository)


@router.post("/calculate", response_model=PaymentCalculationResponse)
async def calculate_payment(
    products: List[ProductItemRequest],
    product_service: ProductService = Depends(get_product_service)
):
    """Розрахунок суми платежу на бекенді"""
    try:
        result = await product_service.calculate_payment(products)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calculation failed: {str(e)}"
        )


def get_payment_service(db: AsyncSession = Depends(get_db)) -> PaymentService:
    """Dependency для отримання сервісу платежів"""
    from app.config import settings
    
    monobank_service = MonobankService(
        store_id=settings.monobank_store_id,
        store_secret=settings.monobank_store_secret
    )
    
    return PaymentService(monobank_service)


@router.post("/validate", response_model=Dict[str, Any])
async def validate_client(
    phone: str,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Валідація клієнта за номером телефону"""
    try:
        result = await payment_service.validate_client(phone)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Client validation failed: {str(e)}"
        )


@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    request: PaymentRequest,
    payment_service: PaymentService = Depends(get_payment_service),
    product_service: ProductService = Depends(get_product_service),
    db: AsyncSession = Depends(get_db)
):
    """Створення платежу"""
    try:
        from app.repositories.payment_repository import PaymentRepository
        from app.repositories.payment_item_repository import PaymentItemRepository
        from app.repositories.customer_repository import CustomerRepository
        from app.services.customer_service import CustomerService
        
        # 1. Розрахувати суми через ProductService
        calculation = await product_service.calculate_payment(request.products)
        
        # 2. Знайти/створити Customer
        customer_repository = CustomerRepository(db)
        customer_service = CustomerService(customer_repository)
        customer = await customer_service.get_or_create_customer(
            phone=request.client_phone,
            first_name=None,
            last_name=None,
            email=None
        )
        
        # 3. Створити Payment в БД
        payment_repository = PaymentRepository(db)
        payment_data = {
            "external_id": None,  # Буде встановлено після Monobank
            "store_order_id": request.store_order_id,
            "customer_id": customer.id,
            "total_sum": calculation.total_sum,
            "status": "pending",
            "invoice_data": request.invoice.json(),
            "products_data": str([p.dict() for p in calculation.products])
        }
        
        payment = await payment_repository.create(payment_data)
        
        # 4. Створити PaymentItem записи в БД
        payment_item_repository = PaymentItemRepository(db)
        created_items = []
        
        for product_data in calculation.products:
            item_data = {
                "payment_id": payment.id,
                "product_id": product_data.product_id,
                "customer_id": customer.id,
                "quantity": product_data.quantity,
                "unit_price": product_data.unit_price,
                "total_price": product_data.total_price
            }
            
            payment_item = await payment_item_repository.create(item_data)
            created_items.append(payment_item)
        
        # 5. Підготувати дані для Monobank
        order_data = {
            "store_order_id": request.store_order_id,
            "client_phone": request.client_phone,
            "total_sum": calculation.total_sum,
            "invoice": request.invoice.dict(),
            "available_programs": [p.dict() for p in request.available_programs],
            "products": [
                {
                    "name": p.name,
                    "count": p.quantity,
                    "sum": p.total_price
                }
                for p in calculation.products
            ],
            "result_callback": request.result_callback
        }
        
        # 6. Відправити в Monobank через PaymentService
        monobank_result = await payment_service.create_payment(order_data)
        
        # 7. Оновити Payment з external_id
        payment.external_id = monobank_result.get("order_id")
        await payment_repository.update(payment)
        
        # 8. Повернути результат
        from app.schemas.payment_item import PaymentItemResponse
        
        return PaymentResponse(
            payment_id=payment.id,
            external_id=payment.external_id,
            status=payment.status,
            total_sum=payment.total_sum,
            products=calculation.products,
            items=[
                PaymentItemResponse.from_attributes(item)
                for item in created_items
            ]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment creation failed: {str(e)}"
        )


@router.get("/{payment_id}/status", response_model=PaymentStatus)
async def get_payment_status(
    payment_id: str,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Отримання статусу платежу"""
    try:
        result = await payment_service.get_payment_status(payment_id)
        return PaymentStatus(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get payment status: {str(e)}"
        )


@router.post("/{payment_id}/confirm")
async def confirm_payment(
    payment_id: str,
    confirmed: bool,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Підтвердження платежу магазином"""
    try:
        result = await payment_service.confirm_payment(payment_id, confirmed)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment confirmation failed: {str(e)}"
        )

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.payment import (
    PaymentRequest, PaymentResponse, PaymentStatus, 
    PaymentCalculationResponse, ProductItemRequest
)
from app.services.payment_service import PaymentService, MonobankService
from app.services.product_service import ProductService
from app.repositories.base import PaymentRepository, ProductRepository
from app.database import get_db
from typing import Dict, Any

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
    monobank_service = MonobankService()
    payment_repository = PaymentRepository(db)
    return PaymentService(payment_repository, monobank_service)


@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    request: PaymentRequest,
    payment_service: PaymentService = Depends(get_payment_service),
    product_service: ProductService = Depends(get_product_service)
):
    """Створення платежу з розрахунком сум на бекенді"""
    try:
        # Спочатку розраховуємо суми
        calculation = await product_service.calculate_payment(request.products)
        
        # Створюємо платеж з розрахованими сумами
        result = await payment_service.create_payment_with_calculation(request, calculation)
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment creation failed: {str(e)}"
        )


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
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Створення платежу"""
    try:
        result = await payment_service.create_payment(request)
        return result
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

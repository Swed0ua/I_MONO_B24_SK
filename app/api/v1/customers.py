from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.services.customer_service import CustomerService
from app.services.crm_service import CRMService, BitrixService
from app.repositories.customer_repository import CustomerRepository
from app.database import get_db
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customers", tags=["customers"])


def get_customer_service(db: AsyncSession = Depends(get_db)) -> CustomerService:
    """Dependency для отримання сервісу клієнтів"""
    customer_repository = CustomerRepository(db)
    return CustomerService(customer_repository)


def get_crm_service() -> CRMService:
    """Dependency для отримання CRM сервісу"""
    bitrix_service = BitrixService()
    return CRMService(bitrix_service)


@router.post("/", response_model=CustomerResponse)
async def create_customer(
    customer_data: CustomerCreate,
    customer_service: CustomerService = Depends(get_customer_service),
    crm_service: CRMService = Depends(get_crm_service)
):
    """Створення клієнта"""
    try:
        # Створюємо клієнта через сервіс
        customer = await customer_service.create_customer(customer_data)
        
        # Створюємо контакт в CRM
        try:
            contact_data = {
                "NAME": customer_data.first_name or "",
                "LAST_NAME": customer_data.last_name or "",
                "PHONE": [{"VALUE": customer_data.phone, "VALUE_TYPE": "WORK"}],
                "EMAIL": [{"VALUE": customer_data.email or "", "VALUE_TYPE": "WORK"}]
            }
            
            crm_result = await crm_service.bitrix_service.create_contact(contact_data)
            if crm_result.get("result"):
                # Оновлюємо клієнта з Bitrix ID
                customer_data_update = CustomerUpdate(bitrix_id=str(crm_result["result"]))
                customer = await customer_service.update_customer(customer.id, customer_data_update)
                
        except Exception as crm_error:
            logger.warning(f"Failed to create CRM contact: {str(crm_error)}")
        
        return customer
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer creation failed: {str(e)}"
        )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Отримання клієнта за ID"""
    customer = await customer_service.get_customer(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return customer


@router.get("/phone/{phone}", response_model=CustomerResponse)
async def get_customer_by_phone(
    phone: str,
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Отримання клієнта за телефоном"""
    customer = await customer_service.get_customer_by_phone(phone)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    customer_service: CustomerService = Depends(get_customer_service),
    crm_service: CRMService = Depends(get_crm_service)
):
    """Оновлення клієнта"""
    try:
        # Оновлюємо через сервіс
        customer = await customer_service.update_customer(customer_id, customer_data)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Оновлюємо в CRM якщо є bitrix_id
        if customer.bitrix_id:
            try:
                await crm_service.update_customer_info(customer.bitrix_id, customer_data.dict())
            except Exception as crm_error:
                logger.warning(f"Failed to update CRM contact: {str(crm_error)}")
        
        return customer
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer update failed: {str(e)}"
        )

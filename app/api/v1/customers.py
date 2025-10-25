from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.dependencies import get_customer_service, get_crm_service
from app.database import get_db
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", response_model=CustomerResponse)
async def create_customer(
    customer_data: CustomerCreate,
    customer_service = Depends(get_customer_service),
    crm_service = Depends(get_crm_service)
):
    """Створення клієнта"""
    try:
        # Передаємо CRMService в CustomerService
        customer_service.crm_service = crm_service
        customer = await customer_service.ensure_customer(customer_data)
        return customer
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Customer creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    customer_service = Depends(get_customer_service)
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
    customer_service = Depends(get_customer_service)
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
    customer_service = Depends(get_customer_service),
    crm_service = Depends(get_crm_service)
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
            status_code=400,
            detail=f"Customer update failed: {str(e)}"
        )

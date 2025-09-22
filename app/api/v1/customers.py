from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.services.crm_service import CRMService, BitrixService
from app.repositories.base import CustomerRepository
from app.database import get_db
from typing import List, Optional

router = APIRouter(prefix="/customers", tags=["customers"])


def get_crm_service() -> CRMService:
    """Dependency для отримання CRM сервісу"""
    bitrix_service = BitrixService()
    return CRMService(bitrix_service)


def get_customer_repository(db: AsyncSession = Depends(get_db)) -> CustomerRepository:
    """Dependency для отримання репозиторію клієнтів"""
    return CustomerRepository(db)


@router.post("/", response_model=CustomerResponse)
async def create_customer(
    customer_data: CustomerCreate,
    crm_service: CRMService = Depends(get_crm_service),
    customer_repo: CustomerRepository = Depends(get_customer_repository)
):
    """Створення клієнта"""
    try:
        # Створюємо в БД
        customer = await customer_repo.create(customer_data.dict())
        
        # Створюємо в CRM
        crm_result = await crm_service.create_customer(customer_data)
        if crm_result.get("result"):
            customer.bitrix_id = str(crm_result["result"])
            await customer_repo.update(customer)
        
        return CustomerResponse.from_orm(customer)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer creation failed: {str(e)}"
        )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    customer_repo: CustomerRepository = Depends(get_customer_repository)
):
    """Отримання клієнта за ID"""
    customer = await customer_repo.get_by_id(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return CustomerResponse.from_orm(customer)


@router.get("/phone/{phone}", response_model=CustomerResponse)
async def get_customer_by_phone(
    phone: str,
    customer_repo: CustomerRepository = Depends(get_customer_repository)
):
    """Отримання клієнта за телефоном"""
    customer = await customer_repo.get_by_phone(phone)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return CustomerResponse.from_orm(customer)


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    crm_service: CRMService = Depends(get_crm_service),
    customer_repo: CustomerRepository = Depends(get_customer_repository)
):
    """Оновлення клієнта"""
    customer = await customer_repo.get_by_id(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    try:
        # Оновлюємо в БД
        update_data = customer_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(customer, key, value)
        
        await customer_repo.update(customer)
        
        # Оновлюємо в CRM якщо є bitrix_id
        if customer.bitrix_id:
            await crm_service.update_customer(customer.bitrix_id, customer_data)
        
        return CustomerResponse.from_orm(customer)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer update failed: {str(e)}"
        )

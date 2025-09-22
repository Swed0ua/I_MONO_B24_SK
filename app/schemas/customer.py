from pydantic import BaseModel, Field
from typing import Optional


class CustomerCreate(BaseModel):
    """Створення клієнта"""
    phone: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class CustomerUpdate(BaseModel):
    """Оновлення клієнта"""
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bitrix_id: Optional[str] = None


class CustomerResponse(BaseModel):
    """Відповідь з даними клієнта"""
    id: int
    phone: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bitrix_id: Optional[str] = None
    created_at: datetime

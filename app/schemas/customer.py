from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class CustomerCreate(BaseModel):
    """Створення клієнта"""
    phone: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bitrix_id: Optional[str] = None
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if not v.startswith('+380'):
            raise ValueError('Phone must start with +380')
        if len(v) != 13:
            raise ValueError('Phone must be 13 characters long')
        return v


class CustomerUpdate(BaseModel):
    """Оновлення клієнта"""
    phone: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bitrix_id: Optional[str] = None
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v is not None:
            if not v.startswith('+380'):
                raise ValueError('Phone must start with +380')
            if len(v) != 13:
                raise ValueError('Phone must be 13 characters long')
        return v


class CustomerResponse(BaseModel):
    """Відповідь з даними клієнта"""
    id: int
    phone: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bitrix_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
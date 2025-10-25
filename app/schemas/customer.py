from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from app.core.validators.validator_factory import ValidatorFactory


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
        validator = ValidatorFactory.create_phone_validator()
        return validator.validate(v)


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
        validator = ValidatorFactory.create_phone_validator()
        return validator.validate_optional(v)


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
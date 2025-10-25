from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class ProductCreate(BaseModel):
    """Створення товару"""
    name: str
    description: Optional[str] = None
    price: float
    sku: str
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class ProductUpdate(BaseModel):
    """Оновлення товару"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    sku: Optional[str] = None
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip() if v else v


class ProductResponse(BaseModel):
    """Відповідь з даними товару"""
    id: int
    name: str
    description: Optional[str] = None
    price: float
    sku: str
    photo: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
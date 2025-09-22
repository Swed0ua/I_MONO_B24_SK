from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class ProductCreate(BaseModel):
    """Створення товару"""
    name: str
    description: Optional[str] = None
    price: float
    sku: str
    category: Optional[str] = None
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @validator('name')
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
    category: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('price')
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @validator('name')
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
    is_active: bool
    category: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

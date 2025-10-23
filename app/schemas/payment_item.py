from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class PaymentItemCreate(BaseModel):
    """Створення товару в платежі"""
    product_id: int
    quantity: int
    unit_price: float
    total_price: float
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v
    
    @field_validator('unit_price')
    @classmethod
    def validate_unit_price(cls, v):
        if v <= 0:
            raise ValueError('Unit price must be positive')
        return v
    
    @field_validator('total_price')
    @classmethod
    def validate_total_price(cls, v):
        if v <= 0:
            raise ValueError('Total price must be positive')
        return v


class PaymentItemUpdate(BaseModel):
    """Оновлення товару в платежі"""
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Quantity must be positive')
        return v
    
    @field_validator('unit_price')
    @classmethod
    def validate_unit_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Unit price must be positive')
        return v
    
    @field_validator('total_price')
    @classmethod
    def validate_total_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Total price must be positive')
        return v


class PaymentItemResponse(BaseModel):
    """Відповідь з даними товару в платежі"""
    id: int
    payment_id: int
    product_id: int
    customer_id: int
    quantity: int
    unit_price: float
    total_price: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PaymentItemWithProductResponse(BaseModel):
    """Відповідь з товаром в платежі та деталями товару"""
    id: int
    payment_id: int
    product_id: int
    customer_id: int
    quantity: int
    unit_price: float
    total_price: float
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

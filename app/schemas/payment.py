from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime


class ProductItemRequest(BaseModel):
    product_id: int
    quantity: int
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v


class ProductItemResponse(BaseModel):
    """Відповідь з інформацією про товар"""
    product_id: int
    name: str
    sku: str
    quantity: int
    unit_price: float
    total_price: float


class InvoiceData(BaseModel):
    """Дані інвойсу"""
    date: str
    number: str
    point_id: int
    source: str = "INTERNET"


class AvailableProgram(BaseModel):
    """Доступна програма розстрочки"""
    available_parts_count: List[int]
    type: str = "payment_installments"


class PaymentRequest(BaseModel):
    """Запит на створення платежу (без сум - розраховується на бекенді)"""
    store_order_id: str
    client_phone: str
    invoice: InvoiceData
    available_programs: List[AvailableProgram]
    products: List[ProductItemRequest]  # Тільки ID та кількість
    result_callback: str
    
    @field_validator('products')
    @classmethod
    def validate_products_not_empty(cls, v):
        if not v:
            raise ValueError('Products list cannot be empty')
        return v


class PaymentCalculationResponse(BaseModel):
    """Відповідь з розрахунком платежу"""
    total_sum: float
    products: List[ProductItemResponse]
    calculated_at: datetime


class PaymentResponse(BaseModel):
    """Відповідь на створення платежу"""
    payment_id: int
    external_id: Optional[str] = None
    status: str
    total_sum: float
    products: List[ProductItemResponse]


class PaymentStatus(BaseModel):
    """Статус платежу"""
    payment_id: int
    external_id: str
    status: str
    is_confirmed: bool
    total_sum: float

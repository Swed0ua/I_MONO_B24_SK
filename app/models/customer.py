from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import BaseModel


class Customer(BaseModel):
    """Customer model"""
    __tablename__ = "customers"
    
    phone = Column(String(20), unique=True, index=True, nullable=False)
    
    email = Column(String(255), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    bitrix_id = Column(String(50), nullable=True)
    
    payments = relationship("Payment", back_populates="customer")
    payment_items = relationship("PaymentItem", back_populates="customer")

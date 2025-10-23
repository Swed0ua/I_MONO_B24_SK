from sqlalchemy import Column, String, Float, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Payment(BaseModel):
    """Payment model"""
    __tablename__ = "payments"
    
    external_id = Column(String(255), unique=True, index=True)
    store_order_id = Column(String(255), index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    total_sum = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    invoice_data = Column(Text)  # JSON
    products_data = Column(Text)  # JSON
    
    customer = relationship("Customer", back_populates="payments")
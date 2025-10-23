from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class PaymentItem(BaseModel):
    """Payment item model - зв'язок між Payment та Product"""
    __tablename__ = "payment_items"
    
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)  # Прямий зв'язок з Customer
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    payment = relationship("Payment", back_populates="items")
    product = relationship("Product", back_populates="payment_items")
    customer = relationship("Customer", back_populates="payment_items")

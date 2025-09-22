from sqlalchemy import Column, String, Float, Boolean, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Customer(BaseModel):
    """Модель клієнта"""
    __tablename__ = "customers"
    
    phone = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(255), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    bitrix_id = Column(String(50), nullable=True)
    
    # Зв'язки
    orders = relationship("Order", back_populates="customer")


class Order(BaseModel):
    """Модель замовлення"""
    __tablename__ = "orders"
    
    external_id = Column(String(255), unique=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), default="created")
    bitrix_deal_id = Column(String(50), nullable=True)
    
    # Зв'язки
    customer = relationship("Customer", back_populates="orders")
    payments = relationship("Payment", back_populates="order")
    order_items = relationship("OrderItem", back_populates="order")


class Payment(BaseModel):
    """Модель платежу"""
    __tablename__ = "payments"
    
    # Основні поля
    external_id = Column(String(255), unique=True, index=True)
    store_order_id = Column(String(255), index=True)
    client_phone = Column(String(20), index=True)
    total_sum = Column(Float, nullable=False)
    
    # Статуси
    status = Column(String(50), default="pending")
    is_confirmed = Column(Boolean, default=False)
    
    # Додаткові дані
    invoice_data = Column(Text)  # JSON
    products_data = Column(Text)  # JSON
    callback_data = Column(Text)  # JSON
    
    # Зв'язки
    order_id = Column(Integer, ForeignKey("orders.id"))
    order = relationship("Order", back_populates="payments")

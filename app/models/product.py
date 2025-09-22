from sqlalchemy import Column, String, Float, Boolean, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Product(BaseModel):
    """Модель товару"""
    __tablename__ = "products"
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    sku = Column(String(100), unique=True, index=True)  # Артикул
    is_active = Column(Boolean, default=True)
    category = Column(String(100), nullable=True)
    
    # Зв'язки
    order_items = relationship("OrderItem", back_populates="product")


class OrderItem(BaseModel):
    """Модель позиції замовлення"""
    __tablename__ = "order_items"
    
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)  # Ціна на момент замовлення
    total_price = Column(Float, nullable=False)  # quantity * unit_price
    
    # Зв'язки
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

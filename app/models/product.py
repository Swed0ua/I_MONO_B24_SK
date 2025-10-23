from sqlalchemy import Column, String, Float, Boolean
from .base import BaseModel


class Product(BaseModel):
    """Product model"""
    __tablename__ = "products"
    
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    sku = Column(String(100), unique=True, index=True)
    description = Column(String(500), nullable=True)
    photo = Column(String(500), nullable=True)
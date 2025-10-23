from sqlalchemy import Column, String, Text
from .base import BaseModel


class Log(BaseModel):
    """Log model"""
    __tablename__ = "logs"
    
    level = Column(String(20), nullable=False)  # INFO, ERROR, DEBUG, WARNING
    message = Column(Text, nullable=False)
    module = Column(String(100), nullable=True)
    data = Column(Text, nullable=True)  # JSON

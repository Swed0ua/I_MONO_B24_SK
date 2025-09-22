from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.schemas.payment import PaymentRequest, PaymentResponse


class PaymentServiceInterface(ABC):
    """Інтерфейс для сервісу платежів"""
    
    @abstractmethod
    async def validate_client(self, phone: str) -> Dict[str, Any]:
        """Валідація клієнта"""
        pass
    
    @abstractmethod
    async def create_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Створення платежу"""
        pass
    
    @abstractmethod
    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Отримання статусу платежу"""
        pass
    
    @abstractmethod
    async def confirm_payment(self, payment_id: str, confirmed: bool) -> Dict[str, Any]:
        """Підтвердження платежу"""
        pass

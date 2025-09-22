from abc import ABC, abstractmethod
from typing import Dict, Any


class NotificationServiceInterface(ABC):
    """Інтерфейс для сервісу повідомлень"""
    
    @abstractmethod
    async def send_payment_notification(self, payment_data: Dict[str, Any]) -> bool:
        """Відправка повідомлення про платеж"""
        pass
    
    @abstractmethod
    async def send_order_notification(self, order_data: Dict[str, Any]) -> bool:
        """Відправка повідомлення про замовлення"""
        pass

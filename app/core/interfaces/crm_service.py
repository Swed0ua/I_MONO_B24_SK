from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CRMServiceInterface(ABC):
    """Інтерфейс для CRM сервісу"""
    
    @abstractmethod
    async def create_customer(self, customer_data: CustomerCreate) -> Dict[str, Any]:
        """Створення клієнта в CRM"""
        pass
    
    @abstractmethod
    async def update_customer(self, customer_id: str, customer_data: CustomerUpdate) -> Dict[str, Any]:
        """Оновлення клієнта в CRM"""
        pass
    
    @abstractmethod
    async def create_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Створення угоди в CRM"""
        pass
    
    @abstractmethod
    async def update_deal(self, deal_id: str, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Оновлення угоди в CRM"""
        pass
    
    @abstractmethod
    async def get_customer_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Пошук клієнта за телефоном"""
        pass

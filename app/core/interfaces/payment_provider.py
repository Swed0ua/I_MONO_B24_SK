from abc import ABC, abstractmethod
from typing import Dict, Any


class PaymentProviderInterface(ABC):
    """Abstract interface for payment providers"""
    
    @abstractmethod
    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create payment order"""
        pass
    
    @abstractmethod
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get order status"""
        pass

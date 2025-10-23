from typing import Dict, Any
from .monobank_service import MonobankService
import logging

logger = logging.getLogger(__name__)


class PaymentService:
    """Payment business logic service"""
    
    def __init__(self, monobank_service: MonobankService):
        self.monobank_service = monobank_service
    
    async def create_payment(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create payment with business logic"""
        try:
            self._validate_order_data(order_data)
            
            result = await self.monobank_service.create_order(order_data)
            
            logger.info(f"Payment created: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Payment creation failed: {str(e)}")
            raise
    
    async def get_payment_status(self, order_id: str) -> Dict[str, Any]:
        """Get payment status"""
        try:
            result = await self.monobank_service.get_order_status(order_id)
            logger.info(f"Payment status for {order_id}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get payment status: {str(e)}")
            raise
    
    def _validate_order_data(self, order_data: Dict[str, Any]) -> None:
        """Validate order data"""
        required_fields = ["store_order_id", "client_phone", "total_sum", "products"]
        
        for field in required_fields:
            if field not in order_data:
                raise ValueError(f"Missing required field: {field}")
        
        if not order_data["products"]:
            raise ValueError("Products list cannot be empty")
        
        if order_data["total_sum"] <= 0:
            raise ValueError("Total sum must be positive")
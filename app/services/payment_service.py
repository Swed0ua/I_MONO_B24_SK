from typing import Dict, Any
from .monobank_service import MonobankService
import logging

logger = logging.getLogger(__name__)


class PaymentService:
    """Payment business logic service"""
    
    def __init__(self, monobank_service: MonobankService):
        self.monobank_service = monobank_service
    

    async def validate_client(self, phone: str) -> Dict[str, Any]:
        """Validate client by phone"""
        try:
            # Basic phone validation
            if not phone.startswith('+380'):
                raise ValueError("Phone must start with +380")
            
            if len(phone) != 13:
                raise ValueError("Phone must be 13 characters long")
            
            return {
                "phone": phone,
                "is_valid": True,
                "message": "Phone number is valid"
            }
            
        except Exception as e:
            logger.error(f"Client validation failed: {str(e)}")
            raise
    
    async def create_payment(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create payment in Monobank with prepared data"""
        try:
            # Відправляємо готові дані в Monobank
            result = await self.monobank_service.create_order(order_data)
            
            logger.info(f"Payment created in Monobank: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Payment creation failed: {str(e)}")
            raise
    
    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Get payment status"""
        try:
            result = await self.monobank_service.get_order_status(payment_id)
            logger.info(f"Payment status for {payment_id}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get payment status: {str(e)}")
            raise
    
    async def confirm_payment(self, payment_id: str, confirmed: bool) -> Dict[str, Any]:
        """Confirm payment"""
        try:
            # Get payment status from Monobank
            status = await self.monobank_service.get_order_status(payment_id)
            
            if confirmed:
                logger.info(f"Payment {payment_id} confirmed by merchant")
            else:
                logger.info(f"Payment {payment_id} rejected by merchant")
            
            return {
                "payment_id": payment_id,
                "confirmed": confirmed,
                "status": status.get("status", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Payment confirmation failed: {str(e)}")
            raise
from typing import Dict, Any
from app.core.interfaces.payment_provider import PaymentProviderInterface
from app.core.validators.validator_factory import ValidatorFactory
import logging

logger = logging.getLogger(__name__)


class PaymentService:
    """Payment business logic service"""
    
    def __init__(self, payment_provider: PaymentProviderInterface):
        self.payment_provider = payment_provider
        self.phone_validator = ValidatorFactory.create_phone_validator()
    

    async def validate_client(self, phone: str) -> Dict[str, Any]:
        """Validate client by phone"""
        try:
            validated_phone = self.phone_validator.validate(phone)
            return {
                "phone": validated_phone,
                "is_valid": True,
                "message": "Phone number is valid"
            }
            
        except ValueError as e:
            logger.error(f"Client validation failed: {str(e)}")
            raise
    
    async def create_payment(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create payment with prepared data"""
        try:
            result = await self.payment_provider.create_order(order_data)
            logger.info(f"Payment created: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Payment creation failed: {str(e)}")
            raise
    
    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Get payment status"""
        try:
            result = await self.payment_provider.get_order_status(payment_id)
            logger.info(f"Payment status for {payment_id}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get payment status: {str(e)}")
            raise
    
    async def confirm_payment(self, payment_id: str, confirmed: bool) -> Dict[str, Any]:
        """Confirm payment"""
        try:
            status = await self.payment_provider.get_order_status(payment_id)
            
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
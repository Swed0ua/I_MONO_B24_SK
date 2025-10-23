from typing import Dict, Any
from .monobank_service import MonobankService
from app.schemas.payment import PaymentRequest, PaymentCalculationResponse
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
    
    async def create_payment_with_calculation(
        self, 
        request: PaymentRequest, 
        calculation: PaymentCalculationResponse
    ) -> Dict[str, Any]:
        """Create payment with calculated amounts"""
        try:
            # Prepare order data for Monobank
            order_data = {
                "store_order_id": request.store_order_id,
                "client_phone": request.client_phone,
                "total_sum": calculation.total_sum,
                "invoice": request.invoice.dict(),
                "available_programs": [p.dict() for p in request.available_programs],
                "products": [
                    {
                        "name": p.name,
                        "count": p.quantity,
                        "sum": p.total_price
                    }
                    for p in calculation.products
                ],
                "result_callback": request.result_callback
            }
            
            # Create payment in Monobank
            result = await self.monobank_service.create_order(order_data)
            
            logger.info(f"Payment created with calculation: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Payment creation with calculation failed: {str(e)}")
            raise
    
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
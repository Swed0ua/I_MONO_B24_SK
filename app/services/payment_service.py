from typing import Dict, Any, List
from .monobank_service import MonobankService
from app.schemas.payment import PaymentRequest, PaymentResponse
from app.repositories.payment_repository import PaymentRepository
from app.repositories.payment_item_repository import PaymentItemRepository
from app.schemas.payment_item import PaymentItemCreate
import logging

logger = logging.getLogger(__name__)


class PaymentService:
    """Payment business logic service"""
    
    def __init__(self, monobank_service: MonobankService, payment_repository: PaymentRepository = None, payment_item_repository: PaymentItemRepository = None):
        self.monobank_service = monobank_service
        self.payment_repository = payment_repository
        self.payment_item_repository = payment_item_repository
    

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
    
    async def create_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Create payment from PaymentRequest"""
        try:
            # Prepare order data for Monobank
            order_data = {
                "store_order_id": request.store_order_id,
                "client_phone": request.client_phone,
                "total_sum": 0.0,  # Will be calculated
                "invoice": request.invoice.dict(),
                "available_programs": [p.dict() for p in request.available_programs],
                "products": [
                    {
                        "name": f"Product {p.product_id}",
                        "count": p.quantity,
                        "sum": 0.0  # Will be calculated
                    }
                    for p in request.products
                ],
                "result_callback": request.result_callback
            }
            
            # Create payment in Monobank
            result = await self.monobank_service.create_order(order_data)
            
            logger.info(f"Payment created: {result}")
            
            # Return PaymentResponse
            return PaymentResponse(
                payment_id=result.get("order_id", 0),
                external_id=result.get("order_id"),
                status=result.get("status", "pending"),
                total_sum=order_data["total_sum"],
                products=[],  # Will be populated by calculation
                items=[]
            )
            
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
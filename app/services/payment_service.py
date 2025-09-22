import hashlib
import hmac
import base64
import json
import httpx
from typing import Dict, Any
from app.core.interfaces.payment_service import PaymentServiceInterface
from app.schemas.payment import PaymentRequest, PaymentResponse, PaymentCalculationResponse, ProductItemResponse
from app.repositories.base import PaymentRepository
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class MonobankService:
    """Сервіс для роботи з Monobank API"""
    
    def __init__(self):
        self.store_id = settings.monobank_store_id
        self.store_secret = settings.monobank_store_secret
        self.base_url = settings.monobank_base_url
    
    def _generate_signature(self, request_body: str) -> str:
        """Генерація HMAC-SHA256 підпису"""
        message_bytes = request_body.encode('utf-8')
        key_bytes = self.store_secret.encode('utf-8')
        
        signature = hmac.new(
            key_bytes,
            message_bytes,
            hashlib.sha256
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    async def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Виконання HTTP запиту до API"""
        url = f"{self.base_url}{endpoint}"
        request_body = json.dumps(data, ensure_ascii=False)
        signature = self._generate_signature(request_body)
        
        headers = {
            'store-id': self.store_id,
            'signature': signature,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=request_body, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def validate_client(self, phone: str) -> Dict[str, Any]:
        """Валідація клієнта"""
        data = {"phone": phone}
        return await self._make_request("/api/client/validate", data)
    
    async def create_order(self, order_data: PaymentRequest) -> Dict[str, Any]:
        """Створення замовлення"""
        data = order_data.dict()
        return await self._make_request("/api/order/create", data)
    
    async def confirm_store(self, order_id: str, confirmed: bool) -> Dict[str, Any]:
        """Підтвердження магазином"""
        data = {
            "order_id": order_id,
            "confirmed": confirmed
        }
        return await self._make_request("/api/order/confirm", data)
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Отримання статусу замовлення"""
        url = f"{self.base_url}/api/order/{order_id}/status"
        headers = {
            'store-id': self.store_id,
            'Accept': 'application/json'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()


class PaymentService(PaymentServiceInterface):
    """Сервіс для роботи з платежами"""
    
    def __init__(self, payment_repository: PaymentRepository, monobank_service: MonobankService):
        self.payment_repository = payment_repository
        self.monobank_service = monobank_service
    
    async def validate_client(self, phone: str) -> Dict[str, Any]:
        """Валідація клієнта"""
        try:
            result = await self.monobank_service.validate_client(phone)
            logger.info(f"Client validation result for {phone}: {result}")
            return result
        except Exception as e:
            logger.error(f"Client validation failed for {phone}: {str(e)}")
            raise
    
    async def create_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Створення платежу"""
        try:
            # Створюємо запис в БД
            payment_data = {
                "store_order_id": request.store_order_id,
                "client_phone": request.client_phone,
                "total_sum": request.total_sum,
                "invoice_data": json.dumps(request.invoice.dict()),
                "products_data": json.dumps([p.dict() for p in request.products]),
                "status": "pending"
            }
            
            payment = await self.payment_repository.create(payment_data)
            
            # Відправляємо запит до Monobank
            monobank_response = await self.monobank_service.create_order(request)
            
            # Оновлюємо запис з відповіддю
            payment.external_id = monobank_response.get("order_id")
            await self.payment_repository.update(payment)
            
            return PaymentResponse(
                payment_id=payment.id,
                external_id=payment.external_id,
                status=payment.status
            )
            
        except Exception as e:
            logger.error(f"Payment creation failed: {str(e)}")
            raise
    
    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Отримання статусу платежу"""
        payment = await self.payment_repository.get_by_external_id(payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        return {
            "payment_id": payment.id,
            "external_id": payment.external_id,
            "status": payment.status,
            "is_confirmed": payment.is_confirmed
        }
    
    async def confirm_payment(self, payment_id: str, confirmed: bool) -> Dict[str, Any]:
        """Підтвердження платежу"""
        payment = await self.payment_repository.get_by_external_id(payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        # Підтверджуємо в Monobank
        result = await self.monobank_service.confirm_store(payment_id, confirmed)
        
        # Оновлюємо статус в БД
        payment.is_confirmed = confirmed
        payment.status = "confirmed" if confirmed else "rejected"
        await self.payment_repository.update(payment)
        
        return result
    
    async def create_payment_with_calculation(
        self, 
        request: PaymentRequest, 
        calculation: PaymentCalculationResponse
    ) -> PaymentResponse:
        """Створення платежу з розрахованими сумами"""
        try:
            # Створюємо запис в БД
            payment_data = {
                "store_order_id": request.store_order_id,
                "client_phone": request.client_phone,
                "total_sum": calculation.total_sum,
                "invoice_data": json.dumps(request.invoice.dict()),
                "products_data": json.dumps([p.dict() for p in calculation.products]),
                "status": "pending"
            }
            
            payment = await self.payment_repository.create(payment_data)
            
            # Підготовлюємо дані для Monobank API (старий формат)
            monobank_request = {
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
            
            # Відправляємо запит до Monobank
            monobank_response = await self.monobank_service.create_order(monobank_request)
            
            # Оновлюємо запис з відповіддю
            payment.external_id = monobank_response.get("order_id")
            await self.payment_repository.update(payment)
            
            return PaymentResponse(
                payment_id=payment.id,
                external_id=payment.external_id,
                status=payment.status,
                total_sum=payment.total_sum,
                products=calculation.products
            )
            
        except Exception as e:
            logger.error(f"Payment creation with calculation failed: {str(e)}")
            raise

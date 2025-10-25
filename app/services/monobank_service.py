import hashlib
import hmac
import base64
import json
import httpx
from typing import Dict, Any
import logging
from app.core.interfaces.payment_provider import PaymentProviderInterface

logger = logging.getLogger(__name__)


class MonobankService(PaymentProviderInterface):
    """Service for Monobank API integration"""
    
    def __init__(self, store_id: str, store_secret: str, base_url: str = "https://u2-demo-ext.mono.st4g3.com"):
        self.store_id = store_id
        self.store_secret = store_secret
        self.base_url = base_url.rstrip('/')
    
    def _generate_signature(self, request_body: str) -> str:
        """Generate HMAC-SHA256 signature"""
        message_bytes = request_body.encode('utf-8')
        key_bytes = self.store_secret.encode('utf-8')
        
        signature = hmac.new(
            key_bytes,
            message_bytes,
            hashlib.sha256
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    async def _make_request(self, endpoint: str, data: Dict[str, Any], method: str = "POST") -> Dict[str, Any]:
        """Make HTTP request to Monobank API"""
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
            if method.upper() == "GET":
                response = await client.get(url, headers=headers)
            else:
                response = await client.post(url, data=request_body, headers=headers)
            
            response.raise_for_status()
            return response.json()
    
    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create payment order"""
        return await self._make_request("/api/order/create", order_data)
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get order status"""
        return await self._make_request(f"/api/order/{order_id}/status", {}, "GET")

import httpx
from typing import Dict, Any, Optional
from app.core.interfaces.crm_service import CRMServiceInterface
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class BitrixService:
    """Сервіс для роботи з Bitrix24 API"""
    
    def __init__(self):
        self.webhook_url = settings.bitrix_webhook_url
    
    async def _make_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Виконання запиту до Bitrix24 API"""
        url = f"{self.webhook_url}{method}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=params or {})
            response.raise_for_status()
            return response.json()
    
    async def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Створення контакту"""
        return await self._make_request("crm.contact.add", {"fields": contact_data})
    
    async def update_contact(self, contact_id: str, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Оновлення контакту"""
        return await self._make_request("crm.contact.update", {
            "id": contact_id,
            "fields": contact_data
        })
    
    async def create_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Створення угоди"""
        return await self._make_request("crm.deal.add", {"fields": deal_data})
    
    async def update_deal(self, deal_id: str, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Оновлення угоди"""
        return await self._make_request("crm.deal.update", {
            "id": deal_id,
            "fields": deal_data
        })
    
    async def get_contact_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Пошук контакту за телефоном"""
        result = await self._make_request("crm.contact.list", {
            "filter": {"PHONE": phone},
            "select": ["ID", "NAME", "LAST_NAME", "PHONE", "EMAIL"]
        })
        
        contacts = result.get("result", [])
        return contacts[0] if contacts else None


class CRMService(CRMServiceInterface):
    """Сервіс для роботи з CRM"""
    
    def __init__(self, bitrix_service: BitrixService):
        self.bitrix_service = bitrix_service
    
    async def create_customer(self, customer_data: CustomerCreate) -> Dict[str, Any]:
        """Створення клієнта в CRM"""
        try:
            contact_data = {
                "NAME": customer_data.first_name or "",
                "LAST_NAME": customer_data.last_name or "",
                "PHONE": [{"VALUE": customer_data.phone, "VALUE_TYPE": "WORK"}],
                "EMAIL": [{"VALUE": customer_data.email, "VALUE_TYPE": "WORK"}] if customer_data.email else []
            }
            
            result = await self.bitrix_service.create_contact(contact_data)
            logger.info(f"Customer created in CRM: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create customer in CRM: {str(e)}")
            raise
    
    async def update_customer(self, customer_id: str, customer_data: CustomerUpdate) -> Dict[str, Any]:
        """Оновлення клієнта в CRM"""
        try:
            contact_data = {}
            if customer_data.first_name:
                contact_data["NAME"] = customer_data.first_name
            if customer_data.last_name:
                contact_data["LAST_NAME"] = customer_data.last_name
            if customer_data.email:
                contact_data["EMAIL"] = [{"VALUE": customer_data.email, "VALUE_TYPE": "WORK"}]
            
            result = await self.bitrix_service.update_contact(customer_id, contact_data)
            logger.info(f"Customer updated in CRM: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to update customer in CRM: {str(e)}")
            raise
    
    async def create_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Створення угоди в CRM"""
        try:
            result = await self.bitrix_service.create_deal(deal_data)
            logger.info(f"Deal created in CRM: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create deal in CRM: {str(e)}")
            raise
    
    async def update_deal(self, deal_id: str, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Оновлення угоди в CRM"""
        try:
            result = await self.bitrix_service.update_deal(deal_id, deal_data)
            logger.info(f"Deal updated in CRM: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to update deal in CRM: {str(e)}")
            raise
    
    async def get_customer_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Пошук клієнта за телефоном"""
        try:
            result = await self.bitrix_service.get_contact_by_phone(phone)
            return result
            
        except Exception as e:
            logger.error(f"Failed to get customer by phone: {str(e)}")
            return None
    
    async def create_deal_from_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Створення угоди з даних платежу"""
        deal_data = {
            "TITLE": f"Payment {payment_data.get('external_id', 'Unknown')}",
            "OPPORTUNITY": payment_data.get("total_sum", 0),
            "CURRENCY_ID": "UAH",
            "STAGE_ID": "NEW",
            "CONTACT_ID": payment_data.get("customer_id"),
            "COMMENTS": f"Payment created from Monobank order: {payment_data.get('external_id')}"
        }
        
        return await self.create_deal(deal_data)

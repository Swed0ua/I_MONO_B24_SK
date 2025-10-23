import httpx
import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class BitrixService:
    """Service for Bitrix24 API integration"""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or settings.bitrix_webhook_url
    
    async def _make_request(self, method: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to Bitrix24 API"""
        url = f"{self.webhook_url}{method}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data or {})
            response.raise_for_status()
            return response.json()
    
    async def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create contact in Bitrix24"""
        try:
            result = await self._make_request("crm.contact.add", {"fields": contact_data})
            logger.info(f"Contact created in Bitrix24: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to create contact in Bitrix24: {str(e)}")
            raise
    
    async def create_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create deal in Bitrix24"""
        try:
            result = await self._make_request("crm.deal.add", {"fields": deal_data})
            logger.info(f"Deal created in Bitrix24: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to create deal in Bitrix24: {str(e)}")
            raise
    
    async def update_contact(self, contact_id: str, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update contact in Bitrix24"""
        try:
            result = await self._make_request("crm.contact.update", {
                "id": contact_id,
                "fields": contact_data
            })
            logger.info(f"Contact updated in Bitrix24: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to update contact in Bitrix24: {str(e)}")
            raise


class CRMService:
    """CRM business logic service"""
    
    def __init__(self, bitrix_service: BitrixService):
        self.bitrix_service = bitrix_service
    
    async def create_customer_lead(self, customer_data: Dict[str, Any], payment_data: Dict[str, Any]) -> str:
        """Create customer lead in CRM"""
        try:
            # Prepare contact data
            contact_data = {
                "NAME": customer_data.get("first_name", ""),
                "LAST_NAME": customer_data.get("last_name", ""),
                "PHONE": [{"VALUE": customer_data["phone"], "VALUE_TYPE": "WORK"}],
                "EMAIL": [{"VALUE": customer_data.get("email", ""), "VALUE_TYPE": "WORK"}]
            }
            
            # Create contact
            contact_result = await self.bitrix_service.create_contact(contact_data)
            contact_id = contact_result.get("result")
            
            # Prepare deal data
            deal_data = {
                "TITLE": f"Payment {payment_data.get('store_order_id', 'Unknown')}",
                "OPPORTUNITY": payment_data.get("total_sum", 0),
                "CURRENCY_ID": "UAH",
                "STAGE_ID": "NEW",
                "CONTACT_ID": contact_id,
                "COMMENTS": f"Payment from Monobank: {payment_data.get('external_id', 'Unknown')}"
            }
            
            # Create deal
            deal_result = await self.bitrix_service.create_deal(deal_data)
            deal_id = deal_result.get("result")
            
            logger.info(f"Customer lead created: Contact {contact_id}, Deal {deal_id}")
            return deal_id
            
        except Exception as e:
            logger.error(f"Failed to create customer lead: {str(e)}")
            raise
    
    async def update_customer_info(self, bitrix_id: str, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer information in CRM"""
        try:
            contact_data = {
                "NAME": customer_data.get("first_name", ""),
                "LAST_NAME": customer_data.get("last_name", ""),
                "PHONE": [{"VALUE": customer_data["phone"], "VALUE_TYPE": "WORK"}],
                "EMAIL": [{"VALUE": customer_data.get("email", ""), "VALUE_TYPE": "WORK"}]
            }
            
            result = await self.bitrix_service.update_contact(bitrix_id, contact_data)
            logger.info(f"Customer info updated in CRM: {bitrix_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to update customer info: {str(e)}")
            raise
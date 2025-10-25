import httpx
import logging
from typing import Dict, Any, Optional
from app.config import settings
from app.core.interfaces.crm_provider import CRMProviderInterface

logger = logging.getLogger(__name__)


class BitrixService(CRMProviderInterface):
    """Bitrix24 CRM provider implementation"""
    
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
    
    async def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """Get contact by ID from Bitrix24"""
        try:
            result = await self._make_request("crm.contact.get", {"id": contact_id})
            logger.info(f"Contact retrieved from Bitrix24: {contact_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to get contact from Bitrix24: {str(e)}")
            raise
    
    async def search_contact_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Search contact by phone number in Bitrix24"""
        try:
            result = await self._make_request("crm.contact.list", {
                "filter": {"PHONE": phone},
                "select": ["ID", "NAME", "LAST_NAME", "PHONE", "EMAIL"]
            })
            
            contacts = result.get("result", [])
            if contacts:
                logger.info(f"Contact found by phone in Bitrix24: {phone}")
                return contacts[0]
            else:
                logger.info(f"No contact found by phone in Bitrix24: {phone}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to search contact by phone in Bitrix24: {str(e)}")
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
    """Universal CRM service that works with any CRM provider"""
    
    def __init__(self, crm_provider: CRMProviderInterface):
        self.crm_provider = crm_provider
    
    async def create_contact_from_customer(self, customer_data) -> Dict[str, Any]:
        """Create CRM contact from CustomerCreate data"""
        contact_data = self._build_contact_data(customer_data)
        return await self.crm_provider.create_contact(contact_data)
    
    async def validate_contact_id_by_phone(self, contact_id: str, phone: str) -> bool:
        """Validate that CRM contact ID matches phone number"""
        try:
            contact = await self.crm_provider.get_contact(contact_id)
            contact_phones = [p["VALUE"] for p in contact.get("PHONE", [])]
            return phone in contact_phones
        except Exception:
            return False
    
    def _build_contact_data(self, customer_data) -> Dict[str, Any]:
        """Build CRM contact data from CustomerCreate - provider agnostic"""
        return {
            "NAME": customer_data.first_name or "",
            "LAST_NAME": customer_data.last_name or "",
            "PHONE": [{"VALUE": customer_data.phone, "VALUE_TYPE": "WORK"}],
            "EMAIL": [{"VALUE": customer_data.email or "", "VALUE_TYPE": "WORK"}] if customer_data.email else []
        }
    
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
            contact_result = await self.crm_provider.create_contact(contact_data)
            contact_id = contact_result.get("result")
            
            logger.info(f"Customer lead created: Contact {contact_id}")
            return contact_id
            
        except Exception as e:
            logger.error(f"Failed to create customer lead: {str(e)}")
            raise
    
    async def update_customer_info(self, contact_id: str, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer information in CRM"""
        try:
            contact_data = {
                "NAME": customer_data.get("first_name", ""),
                "LAST_NAME": customer_data.get("last_name", ""),
                "PHONE": [{"VALUE": customer_data["phone"], "VALUE_TYPE": "WORK"}],
                "EMAIL": [{"VALUE": customer_data.get("email", ""), "VALUE_TYPE": "WORK"}]
            }
            
            result = await self.crm_provider.update_contact(contact_id, contact_data)
            logger.info(f"Customer info updated in CRM: {contact_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to update customer info: {str(e)}")
            raise
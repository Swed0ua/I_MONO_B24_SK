from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class CRMProviderInterface(ABC):
    """Abstract interface for CRM providers"""
    
    @abstractmethod
    async def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create contact in CRM"""
        pass
    
    @abstractmethod
    async def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """Get contact by ID"""
        pass
    
    @abstractmethod
    async def update_contact(self, contact_id: str, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update contact"""
        pass
    
    @abstractmethod
    async def search_contact_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Search contact by phone number"""
        pass

from typing import Dict, Type
from app.core.interfaces.crm_provider import CRMProviderInterface
from app.services.crm_service import BitrixService
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class CRMProviderFactory:
    """Factory for creating CRM providers"""
    
    _providers: Dict[str, Type[CRMProviderInterface]] = {
        "bitrix": BitrixService,
        "salesforce": None,  # Future implementation
        "hubspot": None,     # Future implementation
    }
    
    @classmethod
    def create_provider(cls, provider_type: str, **kwargs) -> CRMProviderInterface:
        """Create CRM provider instance"""
        logger.info(f"Creating CRM provider: {provider_type}")
        
        if provider_type not in cls._providers:
            raise ValueError(f"Unknown CRM provider: {provider_type}")
        
        provider_class = cls._providers[provider_type]
        if provider_class is None:
            raise NotImplementedError(f"CRM provider {provider_type} not implemented yet")
        
        if provider_type == "bitrix":
            return provider_class(
                webhook_url=kwargs.get("webhook_url", settings.bitrix_webhook_url)
            )
        else:
            return provider_class(**kwargs)
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[CRMProviderInterface]):
        """Register new CRM provider type"""
        cls._providers[name] = provider_class
        logger.info(f"Registered new CRM provider: {name}")
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available CRM provider types"""
        return [name for name, provider in cls._providers.items() if provider is not None]

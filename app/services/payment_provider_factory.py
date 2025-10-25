from typing import Dict, Any
from app.core.interfaces.payment_provider import PaymentProviderInterface
from app.services.monobank_service import MonobankService
import logging

logger = logging.getLogger(__name__)


class PaymentProviderFactory:
    """Factory for creating payment providers"""
    
    @staticmethod
    def create_provider(provider_type: str, **kwargs) -> PaymentProviderInterface:
        """Create payment provider instance"""
        logger.info(f"Creating payment provider: {provider_type}")
        
        if provider_type == "monobank":
            return MonobankService(
                store_id=kwargs.get("store_id"),
                store_secret=kwargs.get("store_secret"),
                base_url=kwargs.get("base_url", "https://u2-demo-ext.mono.st4g3.com")
            )
        elif provider_type == "privatbank":
            # Future implementation for Privatbank
            raise NotImplementedError("Privatbank provider not implemented yet")
        else:
            raise ValueError(f"Unknown payment provider: {provider_type}")
    
    @staticmethod
    def get_available_providers() -> list[str]:
        """Get list of available payment providers"""
        return ["monobank", "privatbank"]

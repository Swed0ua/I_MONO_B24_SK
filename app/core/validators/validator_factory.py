from typing import Dict, Type
from app.core.validators.base_validator import BaseValidator
from app.core.validators.phone_validator import PhoneValidator, UkrainianPhoneValidator, InternationalPhoneValidator
import logging

logger = logging.getLogger(__name__)


class ValidatorFactory:
    """Factory for creating validators"""
    
    _validators: Dict[str, Type[BaseValidator]] = {
        "ukrainian_phone": UkrainianPhoneValidator,
        "phone": PhoneValidator,
        "international_phone": InternationalPhoneValidator,
    }
    
    @classmethod
    def create_validator(cls, validator_type: str, **kwargs) -> BaseValidator:
        """Create validator instance"""
        logger.info(f"Creating validator: {validator_type}")
        
        if validator_type not in cls._validators:
            raise ValueError(f"Unknown validator type: {validator_type}")
        
        validator_class = cls._validators[validator_type]
        return validator_class(**kwargs)
    
    @classmethod
    def create_phone_validator(cls, country: str = "UA") -> PhoneValidator:
        """Create phone validator for specific country"""
        if country == "UA":
            return UkrainianPhoneValidator()
        else:
            raise ValueError(f"Unsupported country: {country}")
    
    @classmethod
    def create_international_phone_validator(cls, country_code: str, length: int) -> InternationalPhoneValidator:
        """Create international phone validator"""
        return InternationalPhoneValidator(country_code=country_code, length=length)
    
    @classmethod
    def register_validator(cls, name: str, validator_class: Type[BaseValidator]):
        """Register new validator type"""
        cls._validators[name] = validator_class
        logger.info(f"Registered new validator: {name}")
    
    @classmethod
    def get_available_validators(cls) -> list[str]:
        """Get list of available validator types"""
        return list(cls._validators.keys())

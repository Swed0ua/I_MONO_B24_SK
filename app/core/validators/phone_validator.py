from typing import Optional
from app.core.validators.base_validator import BaseValidator


class PhoneValidator(BaseValidator):
    """Phone number validator with configurable country codes"""
    
    def __init__(self, country_code: str = "+380", length: int = 13):
        self.country_code = country_code
        self.length = length
    
    def validate(self, phone: str) -> str:
        """Validate phone number"""
        if not isinstance(phone, str):
            raise ValueError("Phone must be a string")
        
        if not phone.startswith(self.country_code):
            raise ValueError(f'Phone must start with {self.country_code}')
        
        if len(phone) != self.length:
            raise ValueError(f'Phone must be {self.length} characters long')
        
        return phone
    
    def validate_optional(self, phone: Optional[str]) -> Optional[str]:
        """Validate optional phone number"""
        if phone is not None:
            return self.validate(phone)
        return phone


class UkrainianPhoneValidator(PhoneValidator):
    """Ukrainian phone number validator"""
    
    def __init__(self):
        super().__init__(country_code="+380", length=13)


class InternationalPhoneValidator(PhoneValidator):
    """International phone number validator"""
    
    def __init__(self, country_code: str, length: int):
        super().__init__(country_code=country_code, length=length)

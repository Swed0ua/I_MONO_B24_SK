from enum import Enum

class PaymentProviderType(str, Enum):
    """Payment provider types"""
    MONOBANK = "monobank"
    PRIVATBANK = "privatbank"
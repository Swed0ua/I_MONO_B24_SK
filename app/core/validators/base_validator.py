from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseValidator(ABC):
    """Abstract base class for all validators"""
    
    @abstractmethod
    def validate(self, value: Any) -> Any:
        """Validate a value and return it if valid"""
        pass
    
    @abstractmethod
    def validate_optional(self, value: Optional[Any]) -> Optional[Any]:
        """Validate an optional value"""
        pass

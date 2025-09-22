import hashlib
import hmac
import base64
from typing import Dict, Any
from app.config import settings


def verify_webhook_signature(body: bytes, signature: str) -> bool:
    """Перевірка підпису веб-хука"""
    if not signature:
        return False
    
    expected_signature = hmac.new(
        settings.webhook_secret.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

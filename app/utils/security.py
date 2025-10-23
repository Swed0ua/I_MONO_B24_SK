import hashlib
import hmac
import base64
from typing import Dict, Any
from app.config import settings


def verify_webhook_signature(body: bytes, signature: str) -> bool:
    """Перевірка підпису веб-хука від Monobank"""
    if not signature:
        return False
    
    # Формуємо підпис як Monobank (HMAC-SHA256 + Base64)
    expected_signature = hmac.new(
        settings.monobank_store_secret.encode('utf-8'),
        body,
        hashlib.sha256
    ).digest()
    
    expected_base64 = base64.b64encode(expected_signature).decode('utf-8')
    return hmac.compare_digest(signature, expected_base64)

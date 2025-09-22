from pydantic import BaseModel
from typing import Dict, Any, Optional


class WebhookData(BaseModel):
    """Дані веб-хука"""
    order_id: str
    status: str
    data: Optional[Dict[str, Any]] = None


class MonobankWebhook(BaseModel):
    """Веб-хук від Monobank"""
    order_id: str
    status: str
    callback_data: Optional[Dict[str, Any]] = None


class BitrixWebhook(BaseModel):
    """Веб-хук від Bitrix24"""
    event: str
    data: Dict[str, Any]

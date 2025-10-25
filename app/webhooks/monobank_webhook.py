from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_payment_service
from app.database import get_db
from app.utils.security import verify_webhook_signature
import json
import logging

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


@router.post("/monobank/callback")
async def monobank_callback(
    request: Request,
    payment_service = Depends(get_payment_service)
):
    """Обробка callback від Monobank"""
    try:
        # Отримуємо тіло запиту
        body = await request.body()
        
        # Перевіряємо підпис
        signature = request.headers.get("signature")
        if not verify_webhook_signature(body, signature):
            logger.warning("Invalid webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Парсимо дані
        callback_data = json.loads(body.decode())
        order_id = callback_data.get("order_id")
        status = callback_data.get("status")
        
        logger.info(f"Received Monobank callback: {callback_data}")
        
        # Отримуємо статус платежу через сервіс
        payment_status = await payment_service.get_payment_status(order_id)
        logger.info(f"Payment {order_id} status: {payment_status}")
        
        return {"status": "success", "message": "Callback processed"}
        
    except Exception as e:
        logger.error(f"Monobank callback processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Callback processing failed")

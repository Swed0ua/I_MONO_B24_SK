from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.payment_service import PaymentService
from app.services.monobank_service import MonobankService
from app.repositories.payment_repository import PaymentRepository
from app.database import get_db
from app.config import settings
import json
import logging

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


def get_payment_service(db: AsyncSession = Depends(get_db)) -> PaymentService:
    """Dependency для отримання сервісу платежів"""
    monobank_service = MonobankService(
        store_id=settings.monobank_store_id,
        store_secret=settings.monobank_store_secret
    )
    payment_repository = PaymentRepository(db)
    return PaymentService(monobank_service)


@router.post("/monobank/callback")
async def monobank_callback(
    request: Request,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Обробка callback від Monobank"""
    try:
        # Парсимо дані
        body = await request.body()
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

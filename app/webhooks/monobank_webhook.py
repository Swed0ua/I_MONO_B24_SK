from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.payment_service import PaymentService, MonobankService
from app.services.crm_service import CRMService, BitrixService
from app.repositories.base import PaymentRepository
from app.database import get_db
from app.utils.security import verify_webhook_signature
import json
import logging

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


def get_payment_service(db: AsyncSession = Depends(get_db)) -> PaymentService:
    """Dependency для отримання сервісу платежів"""
    monobank_service = MonobankService()
    payment_repository = PaymentRepository(db)
    return PaymentService(payment_repository, monobank_service)


def get_crm_service() -> CRMService:
    """Dependency для отримання CRM сервісу"""
    bitrix_service = BitrixService()
    return CRMService(bitrix_service)


@router.post("/monobank/callback")
async def monobank_callback(
    request: Request,
    payment_service: PaymentService = Depends(get_payment_service),
    crm_service: CRMService = Depends(get_crm_service)
):
    """Обробка callback від Monobank"""
    try:
        # Перевіряємо підпис
        body = await request.body()
        signature = request.headers.get("signature")
        
        if not verify_webhook_signature(body, signature):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Парсимо дані
        callback_data = json.loads(body.decode())
        order_id = callback_data.get("order_id")
        status = callback_data.get("status")
        
        logger.info(f"Received Monobank callback: {callback_data}")
        
        # Оновлюємо статус платежу
        payment = await payment_service.payment_repository.get_by_external_id(order_id)
        if payment:
            payment.status = status
            payment.callback_data = json.dumps(callback_data)
            await payment_service.payment_repository.update(payment)
            
            # Якщо платеж підтверджено, створюємо угоду в CRM
            if status == "APPROVED":
                deal_data = {
                    "TITLE": f"Payment {order_id}",
                    "OPPORTUNITY": payment.total_sum,
                    "CURRENCY_ID": "UAH",
                    "STAGE_ID": "NEW",
                    "COMMENTS": f"Payment approved from Monobank order: {order_id}"
                }
                await crm_service.create_deal(deal_data)
            
            logger.info(f"Payment {order_id} status updated to {status}")
        
        return {"status": "success", "message": "Callback processed"}
        
    except Exception as e:
        logger.error(f"Monobank callback processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Callback processing failed")


@router.post("/bitrix/callback")
async def bitrix_callback(
    request: Request,
    crm_service: CRMService = Depends(get_crm_service)
):
    """Обробка callback від Bitrix24"""
    try:
        body = await request.body()
        callback_data = json.loads(body.decode())
        
        logger.info(f"Received Bitrix callback: {callback_data}")
        
        event = callback_data.get("event")
        data = callback_data.get("data", {})
        
        if event == "ONCRMDEALUPDATE":
            deal_id = data.get("FIELDS", {}).get("ID")
            logger.info(f"Deal {deal_id} updated in Bitrix24")
        
        elif event == "ONCRMCONTACTADD":
            contact_id = data.get("FIELDS", {}).get("ID")
            logger.info(f"Contact {contact_id} added to Bitrix24")
        
        return {"status": "success", "message": "Bitrix callback processed"}
        
    except Exception as e:
        logger.error(f"Bitrix callback processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Callback processing failed")

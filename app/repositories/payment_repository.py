from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models.payment import Payment


class PaymentRepository:
    """Repository for Payment operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, payment_data: dict) -> Payment:
        """Create payment"""
        payment = Payment(**payment_data)
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment
    
    async def get_by_id(self, payment_id: int) -> Optional[Payment]:
        """Get payment by ID"""
        result = await self.session.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_external_id(self, external_id: str) -> Optional[Payment]:
        """Get payment by external ID"""
        result = await self.session.execute(
            select(Payment).where(Payment.external_id == external_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_store_order_id(self, store_order_id: str) -> Optional[Payment]:
        """Get payment by store order ID"""
        result = await self.session.execute(
            select(Payment).where(Payment.store_order_id == store_order_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_customer_id(self, customer_id: int) -> List[Payment]:
        """Get payments by customer ID"""
        result = await self.session.execute(
            select(Payment).where(Payment.customer_id == customer_id)
        )
        return result.scalars().all()
    
    async def update(self, payment: Payment) -> Payment:
        """Update payment"""
        await self.session.commit()
        await self.session.refresh(payment)
        return payment
    
    async def delete(self, payment_id: int) -> bool:
        """Delete payment"""
        payment = await self.get_by_id(payment_id)
        if payment:
            await self.session.delete(payment)
            await self.session.commit()
            return True
        return False

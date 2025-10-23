from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models.payment_item import PaymentItem


class PaymentItemRepository:
    """Repository for PaymentItem operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, payment_item_data: dict) -> PaymentItem:
        """Create payment item"""
        payment_item = PaymentItem(**payment_item_data)
        self.session.add(payment_item)
        await self.session.commit()
        await self.session.refresh(payment_item)
        return payment_item
    
    async def get_by_id(self, item_id: int) -> Optional[PaymentItem]:
        """Get payment item by ID"""
        result = await self.session.execute(
            select(PaymentItem).where(PaymentItem.id == item_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_payment_id(self, payment_id: int) -> List[PaymentItem]:
        """Get all payment items for a payment"""
        result = await self.session.execute(
            select(PaymentItem).where(PaymentItem.payment_id == payment_id)
        )
        return result.scalars().all()
    
    async def get_by_customer_id(self, customer_id: int) -> List[PaymentItem]:
        """Get all payment items for a customer"""
        result = await self.session.execute(
            select(PaymentItem).where(PaymentItem.customer_id == customer_id)
        )
        return result.scalars().all()
    
    async def get_by_product_id(self, product_id: int) -> List[PaymentItem]:
        """Get all payment items for a product"""
        result = await self.session.execute(
            select(PaymentItem).where(PaymentItem.product_id == product_id)
        )
        return result.scalars().all()
    
    async def update(self, payment_item: PaymentItem) -> PaymentItem:
        """Update payment item"""
        await self.session.commit()
        await self.session.refresh(payment_item)
        return payment_item
    
    async def delete(self, item_id: int) -> bool:
        """Delete payment item"""
        payment_item = await self.get_by_id(item_id)
        if payment_item:
            await self.session.delete(payment_item)
            await self.session.commit()
            return True
        return False
    
    async def delete_by_payment_id(self, payment_id: int) -> int:
        """Delete all payment items for a payment"""
        result = await self.session.execute(
            select(PaymentItem).where(PaymentItem.payment_id == payment_id)
        )
        items = result.scalars().all()
        
        for item in items:
            await self.session.delete(item)
        
        await self.session.commit()
        return len(items)

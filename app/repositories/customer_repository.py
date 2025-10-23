from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models.customer import Customer


class CustomerRepository:
    """Repository for Customer operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, customer_data: dict) -> Customer:
        """Create customer"""
        customer = Customer(**customer_data)
        self.session.add(customer)
        await self.session.commit()
        await self.session.refresh(customer)
        return customer
    
    async def get_by_id(self, customer_id: int) -> Optional[Customer]:
        """Get customer by ID"""
        result = await self.session.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_phone(self, phone: str) -> Optional[Customer]:
        """Get customer by phone"""
        result = await self.session.execute(
            select(Customer).where(Customer.phone == phone)
        )
        return result.scalar_one_or_none()
    
    async def get_by_bitrix_id(self, bitrix_id: str) -> Optional[Customer]:
        """Get customer by Bitrix ID"""
        result = await self.session.execute(
            select(Customer).where(Customer.bitrix_id == bitrix_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[Customer]:
        """Get all customers"""
        result = await self.session.execute(select(Customer))
        return result.scalars().all()
    
    async def update(self, customer: Customer) -> Customer:
        """Update customer"""
        await self.session.commit()
        await self.session.refresh(customer)
        return customer
    
    async def delete(self, customer_id: int) -> bool:
        """Delete customer"""
        customer = await self.get_by_id(customer_id)
        if customer:
            await self.session.delete(customer)
            await self.session.commit()
            return True
        return False

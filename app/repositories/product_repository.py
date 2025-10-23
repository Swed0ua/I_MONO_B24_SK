from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models.product import Product


class ProductRepository:
    """Repository for Product operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, product_data: dict) -> Product:
        """Create product"""
        product = Product(**product_data)
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product
    
    async def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        result = await self.session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """Get product by SKU"""
        result = await self.session.execute(
            select(Product).where(Product.sku == sku)
        )
        return result.scalar_one_or_none()
    
    async def get_all_active(self) -> List[Product]:
        """Get all products"""
        result = await self.session.execute(select(Product))
        return result.scalars().all()
    
    async def update(self, product: Product) -> Product:
        """Update product"""
        await self.session.commit()
        await self.session.refresh(product)
        return product
    
    async def delete(self, product_id: int) -> bool:
        """Delete product"""
        product = await self.get_by_id(product_id)
        if product:
            await self.session.delete(product)
            await self.session.commit()
            return True
        return False

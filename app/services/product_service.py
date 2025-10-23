from typing import List, Optional
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
import logging

logger = logging.getLogger(__name__)


class ProductService:
    """Product service"""
    
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
    
    async def create_product(self, product_data: ProductCreate) -> ProductResponse:
        """Create product"""
        try:
            # Check if SKU already exists
            existing_product = await self.product_repository.get_by_sku(product_data.sku)
            if existing_product:
                raise ValueError(f"Product with SKU {product_data.sku} already exists")
            
            product = await self.product_repository.create(product_data.dict())
            logger.info(f"Product created: {product.name} (SKU: {product.sku})")
            return ProductResponse.from_orm(product)
            
        except Exception as e:
            logger.error(f"Failed to create product: {str(e)}")
            raise
    
    async def get_product(self, product_id: int) -> Optional[ProductResponse]:
        """Get product by ID"""
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            return None
        
        return ProductResponse.from_orm(product)
    
    async def get_all_products(self) -> List[ProductResponse]:
        """Get all products"""
        products = await self.product_repository.get_all_active()
        return [ProductResponse.from_orm(product) for product in products]
    
    async def update_product(self, product_id: int, product_data: ProductUpdate) -> Optional[ProductResponse]:
        """Update product"""
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            return None
        
        try:
            update_data = product_data.dict(exclude_unset=True)
            
            # Check SKU uniqueness if changing
            if 'sku' in update_data and update_data['sku'] != product.sku:
                existing_product = await self.product_repository.get_by_sku(update_data['sku'])
                if existing_product:
                    raise ValueError(f"Product with SKU {update_data['sku']} already exists")
            
            for key, value in update_data.items():
                setattr(product, key, value)
            
            updated_product = await self.product_repository.update(product)
            logger.info(f"Product updated: {updated_product.name} (ID: {updated_product.id})")
            return ProductResponse.from_orm(updated_product)
            
        except Exception as e:
            logger.error(f"Failed to update product: {str(e)}")
            raise
    
    async def delete_product(self, product_id: int) -> bool:
        """Delete product (soft delete)"""
        try:
            result = await self.product_repository.delete(product_id)
            if result:
                logger.info(f"Product deleted (soft): {product_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to delete product: {str(e)}")
            raise
from typing import List, Optional, Dict, Any
from app.repositories.base import ProductRepository, OrderItemRepository
from app.schemas.payment import ProductItemRequest, ProductItemResponse, PaymentCalculationResponse
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ProductService:
    """Сервіс для роботи з товарами"""
    
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
    
    async def create_product(self, product_data: ProductCreate) -> ProductResponse:
        """Створення товару"""
        try:
            # Перевіряємо чи не існує товар з таким SKU
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
        """Отримання товару за ID"""
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            return None
        
        return ProductResponse.from_orm(product)
    
    async def get_all_products(self, active_only: bool = True) -> List[ProductResponse]:
        """Отримання всіх товарів"""
        if active_only:
            products = await self.product_repository.get_all_active()
        else:
            # Якщо потрібно всі товари, додати метод в репозиторій
            products = await self.product_repository.get_all_active()  # Поки що тільки активні
        
        return [ProductResponse.from_orm(product) for product in products]
    
    async def update_product(self, product_id: int, product_data: ProductUpdate) -> Optional[ProductResponse]:
        """Оновлення товару"""
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            return None
        
        try:
            update_data = product_data.dict(exclude_unset=True)
            
            # Перевіряємо SKU на унікальність якщо він змінюється
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
        """Видалення товару (м'яке видалення)"""
        try:
            result = await self.product_repository.delete(product_id)
            if result:
                logger.info(f"Product deleted (soft): {product_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to delete product: {str(e)}")
            raise
    
    async def calculate_payment(self, products: List[ProductItemRequest]) -> PaymentCalculationResponse:
        """Розрахунок суми платежу на основі товарів"""
        calculated_products = []
        total_sum = 0.0
        
        for product_request in products:
            # Отримуємо товар з БД
            product = await self.product_repository.get_by_id(product_request.product_id)
            if not product:
                raise ValueError(f"Product with ID {product_request.product_id} not found")
            
            if not product.is_active:
                raise ValueError(f"Product {product.name} is not active")
            
            # Розраховуємо суму
            unit_price = product.price
            total_price = unit_price * product_request.quantity
            total_sum += total_price
            
            calculated_products.append(ProductItemResponse(
                product_id=product.id,
                name=product.name,
                sku=product.sku,
                quantity=product_request.quantity,
                unit_price=unit_price,
                total_price=total_price
            ))
        
        logger.info(f"Payment calculated: {total_sum} for {len(products)} products")
        return PaymentCalculationResponse(
            total_sum=total_sum,
            products=calculated_products,
            calculated_at=datetime.utcnow()
        )
    
    async def validate_products(self, products: List[ProductItemRequest]) -> bool:
        """Валідація наявності та активності товарів"""
        for product_request in products:
            product = await self.product_repository.get_by_id(product_request.product_id)
            if not product:
                raise ValueError(f"Product with ID {product_request.product_id} not found")
            
            if not product.is_active:
                raise ValueError(f"Product {product.name} is not active")
        
        return True

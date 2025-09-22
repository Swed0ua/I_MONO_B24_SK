from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models.payment import Payment, Order, Customer
from app.models.product import Product, OrderItem


class BaseRepository:
    """Базовий репозиторій"""
    
    def __init__(self, session: AsyncSession):
        self.session = session


class ProductRepository(BaseRepository):
    """Репозиторій для роботи з товарами"""
    
    async def create(self, product_data: dict) -> Product:
        """Створення товару"""
        product = Product(**product_data)
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product
    
    async def get_by_id(self, product_id: int) -> Optional[Product]:
        """Отримання товару за ID"""
        result = await self.session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """Отримання товару за артикулом"""
        result = await self.session.execute(
            select(Product).where(Product.sku == sku)
        )
        return result.scalar_one_or_none()
    
    async def get_all_active(self) -> List[Product]:
        """Отримання всіх активних товарів"""
        result = await self.session.execute(
            select(Product).where(Product.is_active == True)
        )
        return result.scalars().all()
    
    async def update(self, product: Product) -> Product:
        """Оновлення товару"""
        await self.session.commit()
        await self.session.refresh(product)
        return product
    
    async def delete(self, product_id: int) -> bool:
        """Видалення товару (м'яке видалення)"""
        product = await self.get_by_id(product_id)
        if product:
            product.is_active = False
            await self.update(product)
            return True
        return False


class OrderItemRepository(BaseRepository):
    """Репозиторій для роботи з позиціями замовлення"""
    
    async def create(self, order_item_data: dict) -> OrderItem:
        """Створення позиції замовлення"""
        order_item = OrderItem(**order_item_data)
        self.session.add(order_item)
        await self.session.commit()
        await self.session.refresh(order_item)
        return order_item
    
    async def get_by_order_id(self, order_id: int) -> List[OrderItem]:
        """Отримання позицій замовлення за ID замовлення"""
        result = await self.session.execute(
            select(OrderItem).where(OrderItem.order_id == order_id)
        )
        return result.scalars().all()


class PaymentRepository(BaseRepository):
    """Репозиторій для роботи з платежами"""
    
    async def create(self, payment_data: dict) -> Payment:
        """Створення платежу"""
        payment = Payment(**payment_data)
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment
    
    async def get_by_id(self, payment_id: int) -> Optional[Payment]:
        """Отримання платежу за ID"""
        result = await self.session.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_external_id(self, external_id: str) -> Optional[Payment]:
        """Отримання платежу за зовнішнім ID"""
        result = await self.session.execute(
            select(Payment).where(Payment.external_id == external_id)
        )
        return result.scalar_one_or_none()
    
    async def update(self, payment: Payment) -> Payment:
        """Оновлення платежу"""
        await self.session.commit()
        await self.session.refresh(payment)
        return payment


class OrderRepository(BaseRepository):
    """Репозиторій для роботи з замовленнями"""
    
    async def create(self, order_data: dict) -> Order:
        """Створення замовлення"""
        order = Order(**order_data)
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order
    
    async def get_by_id(self, order_id: int) -> Optional[Order]:
        """Отримання замовлення за ID"""
        result = await self.session.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_external_id(self, external_id: str) -> Optional[Order]:
        """Отримання замовлення за зовнішнім ID"""
        result = await self.session.execute(
            select(Order).where(Order.external_id == external_id)
        )
        return result.scalar_one_or_none()


class CustomerRepository(BaseRepository):
    """Репозиторій для роботи з клієнтами"""
    
    async def create(self, customer_data: dict) -> Customer:
        """Створення клієнта"""
        customer = Customer(**customer_data)
        self.session.add(customer)
        await self.session.commit()
        await self.session.refresh(customer)
        return customer
    
    async def get_by_phone(self, phone: str) -> Optional[Customer]:
        """Отримання клієнта за телефоном"""
        result = await self.session.execute(
            select(Customer).where(Customer.phone == phone)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, customer_id: int) -> Optional[Customer]:
        """Отримання клієнта за ID"""
        result = await self.session.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        return result.scalar_one_or_none()

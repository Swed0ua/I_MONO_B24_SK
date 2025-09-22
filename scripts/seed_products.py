#!/usr/bin/env python3
"""
Скрипт для заповнення бази даних тестовими товарами
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
from app.models.base import Base
from app.models.product import Product
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker


async def seed_products():
    """Заповнення тестовими товарами"""
    engine = create_async_engine(settings.database_url)
    
    # Створення таблиць
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Створення сесії
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Тестові товари
        test_products = [
            {
                "name": "Телевизор Samsung 55\"",
                "description": "4K UHD Smart TV з HDR",
                "price": 25000.00,
                "sku": "TV-SAM-55-4K",
                "category": "Електроніка",
                "is_active": True
            },
            {
                "name": "iPhone 15 Pro",
                "description": "Смартфон Apple з камерою 48MP",
                "price": 45000.00,
                "sku": "PHONE-IPHONE-15-PRO",
                "category": "Телефони",
                "is_active": True
            },
            {
                "name": "Ноутбук MacBook Air M2",
                "description": "13-дюймовий ноутбук Apple з чипом M2",
                "price": 55000.00,
                "sku": "LAPTOP-MBA-M2-13",
                "category": "Комп'ютери",
                "is_active": True
            },
            {
                "name": "Навушники AirPods Pro",
                "description": "Бездротові навушники з шумозаглушенням",
                "price": 8500.00,
                "sku": "AUDIO-AIRPODS-PRO",
                "category": "Аксесуари",
                "is_active": True
            },
            {
                "name": "Планшет iPad Air",
                "description": "10.9-дюймовий планшет Apple",
                "price": 28000.00,
                "sku": "TABLET-IPAD-AIR-11",
                "category": "Планшети",
                "is_active": True
            },
            {
                "name": "Кавоварка Delonghi",
                "description": "Автоматична кавоварка з млином",
                "price": 12000.00,
                "sku": "KITCHEN-DELONGHI-CAFE",
                "category": "Побутова техніка",
                "is_active": True
            },
            {
                "name": "Мікрохвильова піч Samsung",
                "description": "Мікрохвильова піч з грилем",
                "price": 8000.00,
                "sku": "KITCHEN-SAM-MICRO-GRILL",
                "category": "Побутова техніка",
                "is_active": True
            },
            {
                "name": "Велосипед Trek Mountain",
                "description": "Гірський велосипед 27.5\"",
                "price": 35000.00,
                "sku": "SPORT-TREK-MTB-275",
                "category": "Спорт",
                "is_active": True
            }
        ]
        
        # Додаємо товари
        for product_data in test_products:
            product = Product(**product_data)
            session.add(product)
        
        await session.commit()
        print(f"Added {len(test_products)} test products to database")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_products())

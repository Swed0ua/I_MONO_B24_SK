#!/usr/bin/env python3
"""
Скрипт для ініціалізації бази даних
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
from app.models.base import Base


async def init_db():
    """Ініціалізація бази даних"""
    engine = create_async_engine(settings.database_url)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database initialized successfully!")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())

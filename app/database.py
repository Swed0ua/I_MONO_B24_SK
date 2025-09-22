from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Створення асинхронного двигуна БД
engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    future=True
)

# Створення фабрики сесій
async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


async def get_db():
    """Dependency для отримання сесії БД"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

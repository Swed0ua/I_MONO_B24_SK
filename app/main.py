from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine
from app.models.base import Base
from app.api.v1 import payments, customers, products
from app.webhooks.monobank_webhook import router as webhook_router
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Створення FastAPI додатку
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="SmartKasa Integration API - Monobank + Bitrix24",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшені обмежити домени
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Підключення роутерів
app.include_router(payments.router, prefix="/api/v1")
app.include_router(customers.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(webhook_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Події при запуску додатку"""
    logger.info("Starting SmartKasa Integration API...")
    
    # Створення таблиць БД
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Події при зупинці додатку"""
    logger.info("Shutting down SmartKasa Integration API...")


@app.get("/")
async def root():
    """Кореневий endpoint"""
    return {
        "message": "SmartKasa Integration API",
        "version": settings.version,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Перевірка здоров'я додатку"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

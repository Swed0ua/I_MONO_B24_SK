from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.payment_service import PaymentService
from app.services.product_service import ProductService
from app.services.customer_service import CustomerService
from app.services.payment_provider_factory import PaymentProviderFactory
from app.services.crm_provider_factory import CRMProviderFactory
from app.services.crm_service import CRMService
from app.repositories.product_repository import ProductRepository
from app.repositories.customer_repository import CustomerRepository
from app.config import settings


def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    """Dependency for ProductService"""
    product_repository = ProductRepository(db)
    return ProductService(product_repository)


def get_payment_service(db: AsyncSession = Depends(get_db)) -> PaymentService:
    """Dependency for PaymentService with configurable provider"""
    provider = PaymentProviderFactory.create_provider(
        provider_type="monobank",
        store_id=settings.monobank_store_id,
        store_secret=settings.monobank_store_secret,
        base_url=settings.monobank_base_url
    )
    return PaymentService(provider)


def get_customer_service(db: AsyncSession = Depends(get_db)) -> CustomerService:
    """Dependency for CustomerService"""
    customer_repository = CustomerRepository(db)
    return CustomerService(customer_repository)


def get_crm_service() -> CRMService:
    """Dependency for CRMService with configurable provider"""
    provider = CRMProviderFactory.create_provider("bitrix")
    return CRMService(provider)


def get_payment_service_with_provider(provider_type: str, **provider_kwargs) -> PaymentService:
    """Dependency for PaymentService with custom provider"""
    provider = PaymentProviderFactory.create_provider(provider_type, **provider_kwargs)
    return PaymentService(provider)

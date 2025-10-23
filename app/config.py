from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App settings
    app_name: str = "SmartKasa Integration"
    debug: bool = False
    version: str = "1.0.0"
    
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost/smartkasa"
    database_echo: bool = False
    
    # Monobank API
    monobank_store_id: str
    monobank_store_secret: str
    monobank_base_url: str = "https://u2-demo-ext.mono.st4g3.com"
    
    # Bitrix24 API
    bitrix_webhook_url: str
    bitrix_client_id: Optional[str] = None
    bitrix_client_secret: Optional[str] = None
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Webhook settings
    webhook_secret: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

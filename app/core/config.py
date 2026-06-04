from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Multi-Tenant SaaS Analytics Platform"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://user:password@localhost/dbname"
    secret_key: str = "your_secret_key_here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    redis_url: str = "redis://localhost:6379"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    cache_ttl: int = 300  # 5 minutes
    stripe_secret_key: str = "sk_test_..."
    stripe_publishable_key: str = "pk_test_..."
    stripe_webhook_secret: str = "whsec_..."

    class Config:
        env_file = ".env"

settings = Settings()
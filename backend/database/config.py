from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import model_validator

from dotenv import load_dotenv
import os

load_dotenv()
class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Ofotolab API"
    APP_VERSION: str = "1.0.0"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: str = os.getenv('APP_PORT')  # Changed to str since it's coming from env
    DEBUG: bool = True
    
    # Database settings
    POSTGRES_USER: str = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_HOST: str = os.getenv('POSTGRES_HOST')
    DB_PORT: int = int(os.getenv('POSTGRES_PORT'))  # Convert to int for DB port
    POSTGRES_DB: str = os.getenv('POSTGRES_DB')
    
    
    # Database pool settings
    DB_ECHO_LOG: bool = True
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY")  # Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: str = "587"  # Changed to str since it's coming from env
    SMTP_USER: str = "your-email@gmail.com"
    SMTP_PASSWORD: str = "your-app-password"
    EMAIL_FROM: str = "Your App <your-email@gmail.com>"

    # AWS settings
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str = "your-bucket-name"

    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"  # Changed to str since it's coming from env
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # Cache settings
    PERMISSION_CACHE_TTL: int = 3600  # 1 hour

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"  # Allow extra fields in env file
        

    def get_database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.DB_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()

__all__ = ["settings"]

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Image Generator API"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Service URLs
    MODEL_SERVICE_URL: str = "http://model_service:8001"
    IMAGE_SERVICE_URL: str = "http://localhost:8002"
    USER_SERVICE_URL: str = "http://image_service:8003"
    
    # Redis settings for service discovery
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # JWT settings
    JWT_SECRET_KEY: str = "your-secret-key"  # Change in production
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "Red Team Command Center"
    APP_VERSION: str = "1.0.0"
    
    DATABASE_URL: str = "sqlite:///./app/db/sql_app.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    HEARTBEAT_TIMEOUT: int = 90
    HEARTBEAT_INTERVAL: int = 30

    class Config:
        env_file = ".env"


settings = Settings()

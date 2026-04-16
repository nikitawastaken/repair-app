"""
Конфигурация приложения из переменных окружения.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""
    
    # База данных
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/repairdb"
    
    # JWT
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 60
    
    # CORS
    cors_origins: list = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()

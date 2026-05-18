from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # База данных
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://postgres:postgres@localhost:5432/repairdb"
    )
    
    # JWT
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # CORS
    _raw_cors = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000"
    )

    cors_origins: list = [
        origin.strip()
        for origin in _raw_cors.split(",")
        if origin.strip()
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()
from pydantic import Field, validator
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # База данных
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/repairdb"
    )

    # Приложение
    app_env: str = Field("development", env="APP_ENV")

    # JWT
    secret_key: str | None = Field(None, env="SECRET_KEY")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    @validator("secret_key", pre=True, always=True)
    def validate_secret_key(cls, value, values):
        environment = values.get("app_env", "development").lower()
        placeholder_keys = {
            None,
            "",
            "your-secret-key-here",
            "your-secret-key-here-change-in-production",
            "dev-secret-key",
        }

        if environment == "production":
            if value in placeholder_keys:
                raise ValueError("SECRET_KEY must be set to a secure, non-default value in production")
            return value

        if value in placeholder_keys:
            return "dev-secret-key"

        return value

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
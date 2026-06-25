"""
Конфигурация для создания тестовых пользователей и вспомогательные функции для тестов.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.user import User, UserRole
from app.services.auth_service import hash_password


# Используется для создания тестовой БД
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


async def get_test_session():
    """Создаёт сессию для тестирования с in-memory БД."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )
    
    # Создаём таблицы
    async with engine.begin() as conn:
        pass  # Миграции применяются отдельно
    
    async_session_maker = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session

"""
Настройка подключения к БД и SessionLocal для работы с SQLModel.
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.config import settings


# Создаём асинхронный движок
engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
)

# Фабрика сессий для асинхронной работы
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    """Генератор сессии БД для внедрения зависимостей."""
    async with async_session_maker() as session:
        yield session


async def init_db():
    """Создание всех таблиц (используется при инициализации)."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def drop_db():
    """Удаление всех таблиц (используется при тестировании)."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

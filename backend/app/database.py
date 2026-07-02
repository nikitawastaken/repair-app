"""
Настройка подключения к БД и SessionLocal для работы с SQLModel.
"""
import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from app.config import settings


# Параметры движка. Под тестами (TESTING=1) используем NullPool: Starlette
# TestClient создаёт новый event loop на каждый запрос, а asyncpg-соединения
# привязаны к loop'у создания — переиспользование пула между loop'ами приводит
# к "another operation is in progress". NullPool открывает свежее соединение
# на каждый запрос и снимает эту проблему. В проде остаётся обычный пул.
engine_kwargs = {"echo": False, "future": True}
if os.getenv("TESTING") == "1":
    engine_kwargs["poolclass"] = NullPool

# Создаём асинхронный движок
engine = create_async_engine(
    settings.database_url,
    **engine_kwargs,
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

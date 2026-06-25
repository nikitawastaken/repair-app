"""
Конфигурация для pytest: фикстуры и общие настройки.
"""
import pytest
from app.database import drop_db, init_db


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Инициализирует БД перед тестами."""
    await init_db()
    yield
    # Cleanup после тестов
    await drop_db()

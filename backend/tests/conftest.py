"""
Конфигурация для pytest: фиксции и общие настройки для фаззинг-тестов.
"""
import pytest
from sqlalchemy import text

from app.database import async_session_maker


# ==================== Очистка БД между тестами ====================

@pytest.fixture(autouse=True)
async def cleanup_db_before_fuzz():
    """Очищает данные из БД ДО каждого примера фаззинга.
    
    Это позволяет избежать конфликтов asyncpg 'another operation in progress'.
    """
    # Перед тестом - очищаем таблицы
    async with async_session_maker() as session:
        try:
            # Очищаем в правильном порядке (учитывая FK)
            await session.execute(text("DELETE FROM tickets"))
            await session.execute(text("DELETE FROM users"))
            await session.commit()
        except Exception:
            pass  # Игнорируем ошибки очистки
    
    yield


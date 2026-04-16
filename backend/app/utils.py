"""
Вспомогательные функции и утилиты для backend.
"""
from datetime import datetime, timezone


def get_current_timestamp():
    """Получает текущее время в UTC."""
    return datetime.now(timezone.utc)


def format_error_message(message: str) -> dict:
    """Форматирует ошибку для API ответа."""
    return {"detail": message}

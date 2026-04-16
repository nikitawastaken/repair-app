"""
Скрипт для создания миграций.
"""
# Добавьте здесь объекты со своими именами для использования
# в операциях миграции.

target_metadata = None  # от models.py

def include_object(object, name, type_, reflected, compare_to):
    """Фильтр для включения/исключения объектов БД в миграциях."""
    return True

"""
Общая конфигурация для Alembic.

Этот файл выполняется контекстом Alembic и обеспечивает
миграции как с использованием автоинкрементного режима (для готового к запуску) 
так и с явным использованием операций.
"""

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Берём конфиг Alembic
config = context.config

# Интерпретируем файл конфига для настройки логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Добавляем модели в 'target_metadata'
from sqlmodel import SQLModel
from app.models.user import User  # noqa
from app.models.ticket import Ticket  # noqa
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в режиме 'offline'."""
    configuration = config.get_section(config.config_ini_section)
    
    # Преобразуем DATABASE_URL из asyncpg в psycopg2
    database_url = os.environ.get("DATABASE_URL", "")
    if database_url:
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    else:
        database_url = configuration.get("sqlalchemy.url")
    
    configuration["sqlalchemy.url"] = database_url

    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск миграций в режиме 'online'."""
    configuration = config.get_section(config.config_ini_section)
    
    # Преобразуем DATABASE_URL из asyncpg в psycopg2
    database_url = os.environ.get("DATABASE_URL", "")
    if database_url:
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    else:
        database_url = configuration.get("sqlalchemy.url")
    
    configuration["sqlalchemy.url"] = database_url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


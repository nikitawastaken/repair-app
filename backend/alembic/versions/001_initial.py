"""Первая миграция: создание таблиц user и ticket

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# Идентификаторы ревизии
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Применить миграцию."""
    # Создаём ENUM типы с проверкой существования
    op.execute("""
        DO $$ 
        BEGIN 
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
                CREATE TYPE userrole AS ENUM ('ADMIN', 'MASTER', 'CLIENT');
            END IF;
        END
        $$;
    """)
    
    op.execute("""
        DO $$ 
        BEGIN 
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ticketstatus') THEN
                CREATE TYPE ticketstatus AS ENUM ('NEW', 'IN_PROGRESS', 'DONE', 'REJECTED');
            END IF;
        END
        $$;
    """)
    
    # Создаём таблицу user (если её нет)
    op.execute("""
            CREATE TABLE IF NOT EXISTS "user" (
            id SERIAL NOT NULL PRIMARY KEY,
            email VARCHAR NOT NULL UNIQUE,
            hashed_password VARCHAR NOT NULL,
            full_name VARCHAR NOT NULL,
            role userrole DEFAULT 'CLIENT' NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL
        );
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_user_email ON "user" (email);
    """)

    # Создаём таблицу ticket (если её нет)
    op.execute("""
        CREATE TABLE IF NOT EXISTS ticket (
            id SERIAL NOT NULL PRIMARY KEY,
            title VARCHAR NOT NULL,
            description VARCHAR NOT NULL,
            status ticketstatus DEFAULT 'NEW' NOT NULL,
            client_id INTEGER NOT NULL REFERENCES "user" (id),
            master_id INTEGER REFERENCES "user" (id),
            created_at TIMESTAMP WITH TIME ZONE NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL
        );
    """)


def downgrade() -> None:
    """Откатить миграцию."""
    op.drop_table('ticket')
    op.drop_table('user')
    
    # Удаляем ENUM типы
    op.execute("DROP TYPE IF EXISTS ticketstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS userrole CASCADE")

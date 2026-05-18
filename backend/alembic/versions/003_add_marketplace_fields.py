"""Add marketplace fields: Ticket (price, address, category), User (is_blocked), update TicketStatus enum

Revision ID: 003_add_marketplace_fields
Revises: 002_convert_timestamps
Create Date: 2026-05-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '003_add_marketplace_fields'
down_revision = '002_convert_timestamps'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем is_blocked к таблице user (проверяем, что колонки не существуют)
    op.execute("""
        DO $$ 
        BEGIN 
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'user' AND column_name = 'is_blocked'
            ) THEN
                ALTER TABLE "user" ADD COLUMN is_blocked BOOLEAN NOT NULL DEFAULT false;
            END IF;
        END
        $$;
    """)

    # Добавляем новые поля к таблице ticket
    op.execute("""
        DO $$ 
        BEGIN 
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'ticket' AND column_name = 'price'
            ) THEN
                ALTER TABLE ticket ADD COLUMN price FLOAT NOT NULL DEFAULT 0.0;
            END IF;
        END
        $$;
    """)
    
    op.execute("""
        DO $$ 
        BEGIN 
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'ticket' AND column_name = 'address'
            ) THEN
                ALTER TABLE ticket ADD COLUMN address VARCHAR NOT NULL DEFAULT '';
            END IF;
        END
        $$;
    """)
    
    op.execute("""
        DO $$ 
        BEGIN 
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'ticket' AND column_name = 'category'
            ) THEN
                ALTER TABLE ticket ADD COLUMN category VARCHAR NOT NULL DEFAULT '';
            END IF;
        END
        $$;
    """)

    # Обновляем ENUM типы для TicketStatus (REJECTED → CANCELLED)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_enum e
                JOIN pg_type t ON e.enumtypid = t.oid
                WHERE t.typname = 'ticketstatus'
                AND e.enumlabel = 'CANCELLED'
            ) THEN
                ALTER TYPE ticketstatus ADD VALUE 'CANCELLED';
            END IF;
        END
        $$;
    """)


def downgrade() -> None:
    # Удаляем новые поля
    op.drop_column('user', 'is_blocked')
    op.drop_column('ticket', 'price')
    op.drop_column('ticket', 'address')
    op.drop_column('ticket', 'category')

    # Откатываем изменения ENUM
    op.execute("""
        DO $$ 
        BEGIN 
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ticketstatus_old') THEN
                CREATE TYPE ticketstatus_old AS ENUM ('NEW', 'IN_PROGRESS', 'DONE', 'REJECTED');
            END IF;
        END
        $$;
    """)
    
    op.execute("ALTER TABLE ticket ALTER COLUMN status DROP DEFAULT")
    op.execute("""
        UPDATE ticket SET status = 'REJECTED' WHERE status = 'CANCELLED'::ticketstatus
    """)
    op.execute("""
        ALTER TABLE ticket ALTER COLUMN status TYPE ticketstatus_old USING status::text::ticketstatus_old
    """)
    op.execute("ALTER TABLE ticket ALTER COLUMN status SET DEFAULT 'NEW'::ticketstatus_old")
    
    op.execute("ALTER TYPE ticketstatus_old RENAME TO ticketstatus_backup")
    op.execute("DROP TYPE ticketstatus")
    op.execute("ALTER TYPE ticketstatus_backup RENAME TO ticketstatus")

"""Convert timestamp columns to timestamptz (with time zone)

Revision ID: 002_convert_timestamps
Revises: 001_initial
Create Date: 2026-05-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_convert_timestamps'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Treat existing naive timestamps as UTC and convert to timestamptz
    op.execute("""
        ALTER TABLE "user"
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
        USING created_at AT TIME ZONE 'UTC';
    """)

    op.execute("""
        ALTER TABLE ticket
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
        USING created_at AT TIME ZONE 'UTC';
    """)

    op.execute("""
        ALTER TABLE ticket
        ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE
        USING updated_at AT TIME ZONE 'UTC';
    """)


def downgrade() -> None:
    # Convert back to timestamp without time zone (drop offset)
    op.execute("""
        ALTER TABLE "user"
        ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE
        USING created_at AT TIME ZONE 'UTC';
    """)

    op.execute("""
        ALTER TABLE ticket
        ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE
        USING created_at AT TIME ZONE 'UTC';
    """)

    op.execute("""
        ALTER TABLE ticket
        ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE
        USING updated_at AT TIME ZONE 'UTC';
    """)

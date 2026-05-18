"""Add sync_metadata table

Revision ID: 0002_add_sync_metadata
Revises: 0001_initial
Create Date: 2026-05-17 23:40:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0003_add_sync_metadata"
down_revision = "0002_remove_raw_json"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "sync_metadata",
        sa.Column("key", sa.String(length=255), primary_key=True, nullable=False),
        sa.Column("value", sa.String(length=2048), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

def downgrade() -> None:
    op.drop_table("sync_metadata")

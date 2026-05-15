"""Remove raw_json columns from all tables

Revision ID: 0002_remove_raw_json
Revises: 0001_initial
Create Date: 2026-05-15 00:00:00.000000
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "0002_remove_raw_json"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE agents DROP COLUMN IF EXISTS raw_json")
    op.execute("ALTER TABLE channels DROP COLUMN IF EXISTS raw_json")
    op.execute("ALTER TABLE agent_metrics DROP COLUMN IF EXISTS raw_json")
    op.execute("ALTER TABLE agent_performance_snapshots DROP COLUMN IF EXISTS raw_json")


def downgrade() -> None:
    op.execute("ALTER TABLE agents ADD COLUMN IF NOT EXISTS raw_json jsonb")
    op.execute("ALTER TABLE channels ADD COLUMN IF NOT EXISTS raw_json jsonb")
    op.execute("ALTER TABLE agent_metrics ADD COLUMN IF NOT EXISTS raw_json jsonb")
    op.execute("ALTER TABLE agent_performance_snapshots ADD COLUMN IF NOT EXISTS raw_json jsonb")

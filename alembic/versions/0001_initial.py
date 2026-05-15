"""Create initial application schema

Revision ID: 0001_initial
Revises: None
Create Date: 2026-05-15 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agents",
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("role", sa.String(), nullable=True),
        sa.Column("queues", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "channels",
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("platform", sa.String(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "queues",
        sa.Column("name", sa.String(), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "agent_metrics",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("chat_id", sa.String(), nullable=True),
        sa.Column("agent_id", sa.String(), sa.ForeignKey("agents.id"), nullable=False),
        sa.Column("queue_name", sa.String(), nullable=True),
        sa.Column("typification", sa.String(), nullable=True),
        sa.Column("openSessions", sa.Integer(), nullable=True),
        sa.Column("closedSessions", sa.Integer(), nullable=True),
        sa.Column("total_agent_responses", sa.Integer(), nullable=True),
        sa.Column("on_hold_count", sa.Integer(), nullable=True),
        sa.Column("transfers_in", sa.Integer(), nullable=True),
        sa.Column("transfers_out", sa.Integer(), nullable=True),
        sa.Column("transfers_out_no_messages", sa.Integer(), nullable=True),
        sa.Column("closed_without_messages", sa.Integer(), nullable=True),
        sa.Column("timeout_no_messages", sa.Integer(), nullable=True),
        sa.Column("agent_timeout_count", sa.Integer(), nullable=True),
        sa.Column("user_timeout_count", sa.Integer(), nullable=True),
        sa.Column("general_session_timeout", sa.Integer(), nullable=True),
        sa.Column("avg_session_attending_time", sa.Float(), nullable=True),
        sa.Column("avg_agent_response_time", sa.Float(), nullable=True),
        sa.Column("total_agent_reaction_time", sa.Float(), nullable=True),
        sa.Column("wait_time_in_queue", sa.Float(), nullable=True),
        sa.Column("wait_time_total_to_first_response", sa.Float(), nullable=True),
        sa.Column("agent_reaction_time_to_first_message", sa.Float(), nullable=True),
        sa.Column("total_duration_from_start_to_first_response", sa.Float(), nullable=True),
        sa.Column("total_duration_from_queue_to_close", sa.Float(), nullable=True),
        sa.Column("agent_active_duration_to_close", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_session_open", sa.Boolean(), nullable=False),
        sa.Column("last_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("session_id", "agent_id", name="uq_session_agent"),
    )

    op.create_table(
        "agent_performance_snapshots",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("agent_email", sa.String(), nullable=True, index=True),
        sa.Column("agent_name", sa.String(), nullable=True),
        sa.Column("role", sa.String(), nullable=True),
        sa.Column("queues", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("state", sa.String(), nullable=True),
        sa.Column("checkin", sa.DateTime(timezone=True), nullable=True),
        sa.Column("checkout", sa.DateTime(timezone=True), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_perf_agent_captured",
        "agent_performance_snapshots",
        ["agent_email", "captured_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_perf_agent_captured", table_name="agent_performance_snapshots")
    op.drop_table("agent_performance_snapshots")
    op.drop_table("agent_metrics")
    op.drop_table("queues")
    op.drop_table("channels")
    op.drop_table("agents")

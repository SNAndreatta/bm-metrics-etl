from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base


class AgentMetric(Base):
    __tablename__ = "agent_metrics"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False, index=True)
    chat_id = Column(String, nullable=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False, index=True)
    queue_name = Column(String, nullable=True)
    typification = Column(String, nullable=True)

    openSessions = Column(Integer, default=0)
    closedSessions = Column(Integer, default=0)
    total_agent_responses = Column(Integer, default=0)
    on_hold_count = Column(Integer, default=0)
    transfers_in = Column(Integer, default=0)
    transfers_out = Column(Integer, default=0)
    transfers_out_no_messages = Column(Integer, default=0)
    closed_without_messages = Column(Integer, default=0)
    timeout_no_messages = Column(Integer, default=0)
    agent_timeout_count = Column(Integer, default=0)
    user_timeout_count = Column(Integer, default=0)
    general_session_timeout = Column(Integer, default=0)

    avg_session_attending_time = Column(Float, default=0.0)
    avg_agent_response_time = Column(Float, default=0.0)
    total_agent_reaction_time = Column(Float, default=0.0)
    wait_time_in_queue = Column(Float, default=0.0)
    wait_time_total_to_first_response = Column(Float, default=0.0)
    agent_reaction_time_to_first_message = Column(Float, default=0.0)
    total_duration_from_start_to_first_response = Column(Float, default=0.0)
    total_duration_from_queue_to_close = Column(Float, default=0.0)
    agent_active_duration_to_close = Column(Float, default=0.0)

    created_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    last_updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    raw_json = Column(JSONB, nullable=True)

    __table_args__ = (
        UniqueConstraint("session_id", "agent_id", name="uq_session_agent"),
    )

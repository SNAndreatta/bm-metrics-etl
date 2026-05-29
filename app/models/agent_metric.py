from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)

from app.core.config import settings
from app.core.database import Base


class AgentMetric(Base):
    __tablename__ = "agent_metrics"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False, index=True)
    chat_id = Column(String, nullable=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False, index=True)
    queue_name = Column(String, nullable=True)
    typification = Column(String, nullable=True)

    openSessions = Column(Integer, nullable=True)
    closedSessions = Column(Integer, nullable=True)
    total_agent_responses = Column(Integer, nullable=True)
    on_hold_count = Column(Integer, nullable=True)
    transfers_in = Column(Integer, nullable=True)
    transfers_out = Column(Integer, nullable=True)
    transfers_out_no_messages = Column(Integer, nullable=True)
    closed_without_messages = Column(Integer, nullable=True)
    timeout_no_messages = Column(Integer, nullable=True)
    agent_timeout_count = Column(Integer, nullable=True)
    user_timeout_count = Column(Integer, nullable=True)
    general_session_timeout = Column(Integer, nullable=True)

    avg_session_attending_time = Column(Float, nullable=True)
    avg_agent_response_time = Column(Float, nullable=True)
    total_agent_reaction_time = Column(Float, nullable=True)
    wait_time_in_queue = Column(Float, nullable=True)
    wait_time_total_to_first_response = Column(Float, nullable=True)
    agent_reaction_time_to_first_message = Column(Float, nullable=True)
    total_duration_from_start_to_first_response = Column(Float, nullable=True)
    total_duration_from_queue_to_close = Column(Float, nullable=True)
    agent_active_duration_to_close = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    is_session_open = Column(Boolean, nullable=False)
    last_updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        UniqueConstraint("session_id", "agent_id", name="uq_session_agent"),
        {"schema": settings.database_schema},
    )

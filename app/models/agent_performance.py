from datetime import datetime, timezone

from sqlalchemy import ARRAY, BigInteger, Column, DateTime, Index, String

from app.core.config import settings
from app.core.database import Base


class AgentPerformanceSnapshot(Base):
    __tablename__ = "agent_performance_snapshots"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    agent_email = Column(String, nullable=True, index=True)
    agent_name = Column(String, nullable=True)
    role = Column(String, nullable=True)
    queues = Column(ARRAY(String), nullable=True)
    state = Column(String, nullable=True)
    checkin = Column(DateTime(timezone=True), nullable=True)
    checkout = Column(DateTime(timezone=True), nullable=True)
    captured_at = Column(
        DateTime(timezone=True),
        index=True,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index("ix_perf_agent_captured", "agent_email", "captured_at"),
        {"schema": settings.database_schema},
    )

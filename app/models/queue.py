from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String

from app.core.database import Base


class Queue(Base):
    __tablename__ = "queues"

    name = Column(String, primary_key=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

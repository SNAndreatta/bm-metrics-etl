import logging
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.models.agent_metric import AgentMetric
from app.models.agent_performance import AgentPerformanceSnapshot
from app.models.channel import Channel
from app.models.queue import Queue
from app.services.etl_mapper import (
    map_agent,
    map_agent_metric,
    map_agent_performance,
    map_channel,
)

logger = logging.getLogger(__name__)


async def upsert_agents(db: AsyncSession, items: list[dict[str, Any]]) -> int:
    count = 0
    for item in items:
        values = map_agent(item)
        stmt = pg_insert(Agent).values(**values).on_conflict_do_update(
            index_elements=["id"],
            set_={
                "name": values["name"],
                "email": values["email"],
                "role": values["role"],
                "queues": values["queues"],
                "raw_json": values["raw_json"],
                "updated_at": text("NOW()"),
            },
        )
        await db.execute(stmt)
        count += 1
    await db.commit()
    return count


async def upsert_channels(db: AsyncSession, items: list[dict[str, Any]]) -> int:
    count = 0
    for item in items:
        values = map_channel(item)
        stmt = pg_insert(Channel).values(**values).on_conflict_do_update(
            index_elements=["id"],
            set_={
                "name": values["name"],
                "platform": values["platform"],
                "active": values["active"],
                "raw_json": values["raw_json"],
                "updated_at": text("NOW()"),
            },
        )
        await db.execute(stmt)
        count += 1
    await db.commit()
    return count


async def upsert_agent_metrics(db: AsyncSession, items: list[dict[str, Any]], session_status: str = "open") -> int:
    count = 0
    
    # If session_status is "closed", mark all records with these session_ids as closed
    if session_status == "closed":
        session_ids = [item.get("session_id") for item in items if item.get("session_id")]
        if session_ids:
            stmt = text(
                f"UPDATE agent_metrics SET is_session_opened = FALSE WHERE session_id = ANY(:session_ids)"
            )
            await db.execute(stmt, {"session_ids": session_ids})
            await db.commit()
    
    # Upsert each metric record with the appropriate session_status
    for item in items:
        values = map_agent_metric(item, session_status=session_status)
        stmt = pg_insert(AgentMetric).values(**values).on_conflict_do_update(
            index_elements=["session_id", "agent_id"],
            set_={
                k: v for k, v in values.items() if k not in ("session_id", "agent_id", "id")
            },
        )
        await db.execute(stmt)
        count += 1
    await db.commit()
    return count


async def insert_agent_performance_snapshots(db: AsyncSession, items: list[dict[str, Any]]) -> int:
    count = 0
    for item in items:
        values = map_agent_performance(item)
        db.add(AgentPerformanceSnapshot(**values))
        count += 1
    await db.commit()
    return count


async def sync_queues(db: AsyncSession, queue_names: set[str]) -> int:
    count = 0
    for name in queue_names:
        if not name:
            continue
        existing = await db.execute(select(Queue).where(Queue.name == name))
        if not existing.scalar_one_or_none():
            db.add(Queue(name=name))
            count += 1
    if count:
        await db.commit()
    return count

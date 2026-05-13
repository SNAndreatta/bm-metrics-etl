import logging
from datetime import datetime, timedelta, timezone

from app.clients.botmaker_client import BotmakerClient
from app.core.config import settings
from app.core.database import async_session_factory
from app.services.data_ingestion import (
    insert_agent_performance_snapshots,
    sync_queues,
    upsert_agent_metrics,
    upsert_agents,
    upsert_channels,
)

logger = logging.getLogger(__name__)

WINDOW_DAYS = 1


async def run_backfill() -> None:
    days = settings.retrieval_interval_days
    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=days)

    logger.info("Starting backfill from %s to %s", date_from.isoformat(), now.isoformat())

    async with BotmakerClient() as client:
        agents_raw = await client.list_agents()
        channels_raw = await client.list_channels(active=True)

    async with async_session_factory() as db:
        agent_count = await upsert_agents(db, agents_raw)
        channel_count = await upsert_channels(db, channels_raw)
        all_queues: set[str] = set()
        for agent in agents_raw:
            for q in (agent.get("queues") or []):
                if q:
                    all_queues.add(q)
        q_count = await sync_queues(db, all_queues)
        logger.info("Seeded %s agents, %s channels, %s queues", agent_count, channel_count, q_count)

    current = date_from
    total_metrics = 0
    total_perf = 0

    while current < now:
        window_end = min(current + timedelta(days=WINDOW_DAYS), now)

        async with BotmakerClient() as client:
            metrics_open = await client.list_agent_metrics(from_dt=current, to_dt=window_end, session_status="open")
            metrics_closed = await client.list_agent_metrics(from_dt=current, to_dt=window_end, session_status="closed")
            metrics_raw = metrics_open + metrics_closed
            perf_raw = await client.list_agent_performance(from_dt=current, to_dt=window_end)

        async with async_session_factory() as db:
            m_count = await upsert_agent_metrics(db, metrics_raw)
            p_count = await insert_agent_performance_snapshots(db, perf_raw)
            total_metrics += m_count
            total_perf += p_count

        logger.info(
            "Backfill window %s — %s: %s metrics, %s perf snapshots",
            current.isoformat(), window_end.isoformat(), m_count, p_count,
        )
        current = window_end

    logger.info("Backfill complete — %s metrics, %s perf snapshots", total_metrics, total_perf)

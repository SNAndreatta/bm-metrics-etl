import logging
from datetime import datetime, timedelta, timezone

from app.clients.botmaker_client import BotmakerClient
from app.core.database import async_session_factory
from app.services.data_ingestion import (
    insert_agent_performance_snapshots,
    sync_queues,
    upsert_agent_metrics,
    upsert_agents,
    upsert_channels,
)

FETCH_WINDOW_MINUTES = 6
logger = logging.getLogger(__name__)


async def sync_all_endpoints() -> None:
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=FETCH_WINDOW_MINUTES)

    async with BotmakerClient() as client:
        agents_raw = await client.list_agents()
        channels_raw = await client.list_channels(active=True)
        metrics_open = await client.list_agent_metrics(from_dt=window_start, to_dt=now, session_status="open")
        metrics_closed = await client.list_agent_metrics(from_dt=window_start, to_dt=now, session_status="closed")
        metrics_raw = metrics_open + metrics_closed
        perf_raw = await client.list_agent_performance(from_dt=window_start, to_dt=now)

    async with async_session_factory() as db:
        agent_count = await upsert_agents(db, agents_raw)
        logger.info("Synced %s agents", agent_count)

        channel_count = await upsert_channels(db, channels_raw)
        logger.info("Synced %s channels", channel_count)

        metric_count = await upsert_agent_metrics(db, metrics_raw)
        logger.info("Synced %s agent metrics", metric_count)

        perf_count = await insert_agent_performance_snapshots(db, perf_raw)
        logger.info("Synced %s agent performance snapshots", perf_count)

        all_queues: set[str] = set()
        for agent in agents_raw:
            for q in (agent.get("queues") or []):
                if q:
                    all_queues.add(q)
        q_count = await sync_queues(db, all_queues)
        if q_count:
            logger.info("Added %s new queues", q_count)

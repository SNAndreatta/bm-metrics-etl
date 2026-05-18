import logging
from datetime import datetime, timedelta, timezone

from app.clients.botmaker_client import BotmakerClient
from app.core.database import async_session_factory
from app.core.timestamp_manager import (
    get_last_sync_timestamp,
    update_last_sync_timestamp,
)
from app.services.data_ingestion import (
    insert_agent_performance_snapshots,
    sync_queues,
    upsert_agent_metrics,
    upsert_agents,
    upsert_channels,
)

logger = logging.getLogger(__name__)


async def sync_all_endpoints() -> None:
    async with async_session_factory() as db:
        now = datetime.now(timezone.utc)
        
        # Try to use last sync timestamp as window start, fallback to configured interval
        last_sync = await get_last_sync_timestamp(db)
        if last_sync is not None:
            window_start = last_sync
            logger.info("Resuming sync from last sync timestamp: %s", last_sync.isoformat())
        else:
            # Fallback to configured fetch interval (convert seconds to timedelta)
            from app.core.config import settings
            window_start = now - timedelta(seconds=settings.fetch_interval_seconds)
            logger.info(
                "First sync or no prior timestamp, using default fetch interval (%d seconds)",
                settings.fetch_interval_seconds,
            )

        async with BotmakerClient() as client:
            agents_raw = await client.list_agents()
            channels_raw = await client.list_channels(active=True)
            metrics_open = await client.list_agent_metrics(from_dt=window_start, to_dt=now, session_status="open")
            metrics_closed = await client.list_agent_metrics(from_dt=window_start, to_dt=now, session_status="closed")
            metrics_raw = metrics_open + metrics_closed
            perf_raw = await client.list_agent_performance(from_dt=window_start, to_dt=now)

        agent_count = await upsert_agents(db, agents_raw)
        logger.info("Synced %s agents", agent_count)

        channel_count = await upsert_channels(db, channels_raw)
        logger.info("Synced %s channels", channel_count)

        # Upsert open sessions
        if metrics_open:
            metric_count_open = await upsert_agent_metrics(db, metrics_open, session_status="open")
            logger.info("Synced %s open agent metrics", metric_count_open)
        
        # Upsert closed sessions (this will also mark all related sessions as closed)
        if metrics_closed:
            metric_count_closed = await upsert_agent_metrics(db, metrics_closed, session_status="closed")
            logger.info("Synced %s closed agent metrics", metric_count_closed)

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
        
        # Update last sync timestamp after successful sync
        await update_last_sync_timestamp(db, now)
        logger.info("Sync completed successfully")

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings

logger = logging.getLogger(__name__)

scheduler: AsyncIOScheduler | None = None
backfill_complete = asyncio.Event()


def setup_scheduler() -> AsyncIOScheduler:
    global scheduler
    scheduler = AsyncIOScheduler()
    return scheduler


def start_sync_job() -> None:
    from app.tasks.sync import sync_all_endpoints

    if scheduler is None:
        raise RuntimeError("Scheduler not set up")
    interval = settings.fetch_interval_seconds
    scheduler.add_job(sync_all_endpoints, "interval", seconds=interval, id="sync_job", replace_existing=True)
    logger.info("Sync job scheduled every %s seconds", interval)


def shutdown_scheduler() -> None:
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down")

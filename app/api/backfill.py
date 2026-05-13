import logging

from fastapi import APIRouter

from app.tasks.backfill import run_backfill
from app.tasks.scheduler import backfill_complete, scheduler

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/backfill", tags=["backfill"])

_backfill_running = False


@router.post("/trigger")
async def trigger_backfill():
    global _backfill_running
    if _backfill_running:
        return {"status": "skipped", "message": "Backfill already running"}

    _backfill_running = True
    backfill_complete.clear()

    logger.info("Manual backfill triggered")
    try:
        await run_backfill()
        backfill_complete.set()
        if scheduler and not scheduler.running:
            scheduler.start()
        return {"status": "completed", "message": "Backfill finished"}
    finally:
        _backfill_running = False


@router.get("/status")
async def backfill_status():
    return {
        "running": _backfill_running,
        "completed": backfill_complete.is_set(),
    }

import logging

from fastapi import APIRouter

from app.tasks.backfill import run_backfill

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/backfill", tags=["backfill"])

_backfill_running = False


@router.post("/trigger")
async def trigger_backfill():
    global _backfill_running
    if _backfill_running:
        return {"status": "skipped", "message": "Backfill already running"}

    _backfill_running = True
    logger.info("Manual corrective re-sync triggered")
    try:
        await run_backfill()
        return {"status": "completed", "message": "Corrective re-sync finished"}
    finally:
        _backfill_running = False


@router.get("/status")
async def backfill_status():
    return {"running": _backfill_running}

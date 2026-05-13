from datetime import datetime, timezone

from fastapi import APIRouter

from app.tasks.scheduler import backfill_complete, scheduler

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "backfill_complete": backfill_complete.is_set(),
        "scheduler_running": scheduler is not None and scheduler.running,
    }

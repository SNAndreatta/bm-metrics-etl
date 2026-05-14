from datetime import datetime, timezone

from fastapi import APIRouter

import app.tasks.scheduler as scheduler_module

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    sched = scheduler_module.scheduler
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scheduler_running": sched is not None and sched.running,
    }

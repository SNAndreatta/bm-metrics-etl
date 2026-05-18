import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models  # noqa: F401

from app.api.health import router as health_router
from app.core.database import Base, engine
from app.tasks.scheduler import (
    shutdown_scheduler,
    start_sync_job,
    setup_scheduler,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    sched = setup_scheduler()
    start_sync_job()
    sched.start()
    logger.info("Scheduler started")
    
    yield
    
    shutdown_scheduler()
    await engine.dispose()


app = FastAPI(title="Botmaker Orchestrator", lifespan=lifespan)

app.include_router(health_router)

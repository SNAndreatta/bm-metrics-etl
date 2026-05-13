import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.backfill import router as backfill_router
from app.api.health import router as health_router
from app.core.database import Base, engine
from app.tasks.backfill import run_backfill
from app.tasks.scheduler import (
    backfill_complete,
    shutdown_scheduler,
    start_sync_job,
    setup_scheduler,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Running backfill...")
    await run_backfill()
    backfill_complete.set()
    logger.info("Backfill complete")

    sched = setup_scheduler()
    start_sync_job()
    sched.start()
    logger.info("Scheduler started")

    yield

    shutdown_scheduler()
    await engine.dispose()


app = FastAPI(title="Botmaker Orchestrator", lifespan=lifespan)

app.include_router(health_router)
app.include_router(backfill_router)

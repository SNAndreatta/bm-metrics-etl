import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

# Ensure app package is importable when running alembic from repo root
sys.path.insert(0, os.getcwd())

from app.core.config import settings
from app.core.database import Base
from app.models.agent import Agent  # noqa: F401
from app.models.agent_metric import AgentMetric  # noqa: F401
from app.models.agent_performance import AgentPerformanceSnapshot  # noqa: F401
from app.models.channel import Channel  # noqa: F401
from app.models.queue import Queue  # noqa: F401

config = context.config
fileConfig(config.config_file_name)

# Override sqlalchemy.url with app settings
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=settings.database_schema,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection, 
        target_metadata=target_metadata,
        version_table_schema=settings.database_schema,
        include_schemas=True,
    )


    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

# Alembic migrations for Botmaker Orchestrator

This project uses Alembic to manage database schema changes for the PostgreSQL backend.

## What was added

- `alembic.ini`: Alembic configuration file.
- `alembic/env.py`: migration environment that loads the app's metadata and uses `app.core.config.settings.database_url`.
- `alembic/versions/0001_initial.py`: initial schema migration for all app tables.

## Why this fixes the problem

The app previously used `Base.metadata.create_all()` in `app/main.py`, but the SQLAlchemy model classes were not imported before table creation. That means the metadata did not include `agents`, `channels`, `agent_metrics`, etc., so the database schema was incomplete and the app raised `UndefinedTableError`.

Alembic solves this by:

1. Providing a dedicated schema versioning system.
2. Generating a migration script that explicitly creates the required tables.
3. Keeping the schema in sync with the Python models over time.

## How to use it

### Run migrations locally with Poetry

If you run Alembic from your host machine, the DB hostname `db` is only resolvable from inside Docker. Run Alembic from the API container instead:

```bash
cd /root/botmaker_prueba
docker compose exec api poetry run alembic upgrade head
```

### Rebuild the database and apply migrations

If you are resetting the DB volume, use:

```bash
docker compose down -v
docker compose up -d
poetry run alembic upgrade head
```

### If you need to inspect migration history

```bash
poetry run alembic history --verbose
```

## Notes

- `alembic/env.py` imports the model modules explicitly so `Base.metadata` contains the full schema.
- Future schema changes should be added with `poetry run alembic revision --autogenerate -m "message"`.
- If you change models, run `alembic upgrade head` after creating the new revision.

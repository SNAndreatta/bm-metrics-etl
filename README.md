# Botmaker Data Orchestrator

ETL pipeline that extracts metrics from the Botmaker API v2.0, transforms them, and loads them into PostgreSQL for consumption by Metabase or any other analytics tool.

## Architecture

```
Botmaker API v2.0  ──►  BotmakerClient (httpx async)  ──►  ETL Mapper  ──►  PostgreSQL
                                                                              │
                                                                         Metabase
```

- **Backfill**: Pulls historical data in 1-day sliding windows over a configurable interval (default: 5 days). Runs once at startup.
- **Sync**: Continuously pulls new data every N seconds (default: 60) using a 4-minute lookback window to avoid missing records.
- **Gate**: Sync only starts after backfill completes (`backfill_complete` flag).
- **Auth**: JWT tokens auto-refresh via `POST /auth/credentials` when expired.

## Quick Start

### 1. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

Variables de botmaker: https://go.botmaker.com/#/api/

| Variable | Description | Required |
|---|---|---|
| `BOTMAKER_ACCESS_TOKEN` | JWT access token from Botmaker dashboard | Yes |
| `CLIENT_ID` | Botmaker client ID (e.g. `telviso`) | Yes |
| `SECRET_ID` | Botmaker secret ID | Yes |
| `REFRESH_TOKEN` | JWT refresh token from Botmaker dashboard | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `FETCH_INTERVAL_SECONDS` | Sync interval (default: `60`) | No |
| `RETRIEVAL_INTERVAL_DAYS` | Backfill window in days (default: `5`) | No |

### 2. Run with Docker (recommended)

```bash
docker compose up --build
```

This starts:
- `api` — FastAPI app with the ETL pipeline
- `db` — PostgreSQL 16 (ephemeral unless volume is configured)

Tables are auto-created on startup. Backfill runs immediately. Sync starts after backfill.

### 3. Check status

```bash
curl http://localhost:8000/health
curl http://localhost:8000/backfill/status
```

### 4. Trigger manual backfill

```bash
curl -X POST http://localhost:8000/backfill/trigger
```

## Connecting to an External PostgreSQL

### Option A: Use an existing PostgreSQL instance

Set `DATABASE_URL` to point to your database:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
```

The pipeline uses `asyncpg` as the driver, so the URL scheme must be `postgresql+asyncpg://`.

Example for a managed cloud database:

```env
DATABASE_URL=postgresql+asyncpg://admin:secret@my-db-instance.aws.com:5432/botmaker
```

> The `+asyncpg` part is important — SQLAlchemy needs it to select the async driver.

### Option B: Run with Docker + external DB

```yaml
# docker-compose.override.yml
services:
  api:
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname
```

Then start only the API container (no local Postgres):

```bash
docker compose up api
```

### Option C: Run without Docker (local dev)

```bash
poetry install
poetry run python -m app.main
```

Set `DATABASE_URL` to any reachable PostgreSQL.

## Database Schema

### Tables created automatically

| Table | Description | Key |
|---|---|---|
| `agents` | Botmaker agents | `id` (PK) |
| `channels` | Communication channels | `id` (PK) |
| `queues` | Queue names extracted from agents | `name` (unique) |
| `agent_metrics` | Session metrics per agent | `(session_id, agent_id)` unique |
| `agent_performance_snapshots` | Daily agent performance | auto-increment PK, append-only |

All tables include a `raw_json` JSONB column with the original API payload.

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check + backfill/scheduler status |
| `POST` | `/backfill/trigger` | Trigger a new backfill |
| `GET` | `/backfill/status` | Check if backfill is running/completed |

## Development

### Run tests

```bash
poetry run pytest
```

### Project structure

```
app/
├── main.py                 # FastAPI app, lifespan, startup
├── core/
│   ├── config.py           # pydantic-settings (reads .env)
│   └── database.py         # Async SQLAlchemy engine + session
├── models/
│   ├── agent.py
│   ├── channel.py
│   ├── queue.py
│   ├── agent_metric.py
│   └── agent_performance.py
├── clients/
│   ├── botmaker_client.py  # HTTP client with retry + auth refresh
│   ├── exceptions.py
│   └── auth.py             # JWT expiry check
├── services/
│   ├── etl_mapper.py       # API → DB field mapping + type casting
│   └── data_ingestion.py   # Upsert/insert via ON CONFLICT
├── tasks/
│   ├── backfill.py         # Historical data pull
│   ├── sync.py             # Continuous incremental sync
│   └── scheduler.py        # AsyncIOScheduler setup
├── api/
│   └── routes.py           # /health, /backfill/trigger, /backfill/status
└── tests/
    ├── test_client.py
    ├── test_mapper.py
    ├── test_auth.py
    └── test_ingestion.py
```

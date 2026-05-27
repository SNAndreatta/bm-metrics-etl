# Botmaker Data Orchestrator — Final Implementation Plan (v2)

## 1. Project Infrastructure

- **Dependency Management**: Poetry (fastapi, sqlalchemy[asyncio], asyncpg, alembic, pydantic-settings, apscheduler, httpx, python-dateutil)
- **Containerization**: docker-compose.yml with `api` (FastAPI) + `db` (postgres:16-alpine), health checks, named volume
- **Database Engine**: SQLAlchemy 2.0 **async** + **asyncpg** driver (not psycopg2). JSONB columns for raw payloads.

## 2. Environment Variables

| Variable | Description |
|---|---|
| BOTMAKER_ACCESS_TOKEN | JWT access token for Botmaker API (expires ~5y, auto-renewed) |
| CLIENT_ID | Client Id from Botmaker platform |
| SECRET_ID | Secret ID from Botmaker platform |
| REFRESH_TOKEN | JWT refresh token to get new credentials |
| DATABASE_URL | PostgreSQL async URL (`postgresql+asyncpg://...`) |
| FETCH_INTERVAL_SECONDS | Sync interval (default 60) |
| RETRIEVAL_INTERVAL_DAYS | Backfill depth in days (default 30) |

## 3. ETL Workflow

### Phase 1: Initial Boot & Backfill
- On cold start, compute `[now - RETRIEVAL_INTERVAL_DAYS, now]`
- Fetch **List Agent Metrics** and **List Agent Performance** in sliding 1-day windows
- Handle all `nextPage` tokens recursively per window
- Each window is independently retriable (status tracking)
- **Backfill must complete before Phase 2 begins** — gated by a `backfill_complete` flag

### Phase 2: Continuous Sync (1-Minute Task)
- APScheduler `AsyncIOScheduler` triggers every `FETCH_INTERVAL_SECONDS`
- Fetches 4 endpoints independently; failure of one does not block others
- **List Agents**: upsert by `id`; extract `queues` array → populate Agent.queues (ARRAY column) + seed Queue table
- **List Channels**: upsert by `id`; optionally filter active=true
- **List Agent Metrics**: upsert by `(session_id, agent_id)` composite key (unique constraint). Transfer = new row. All metric fields are strings from API → cast to int/float via `int()`/`float()`.
- **List Agent Performance**: append-only insert per agent per cycle (no upsert). Includes `checkout` column.

## 4. Pagination Handling
- Generic `_paginated_get()` method: loop while `nextPage` is non-null
- Also supports non-paginated responses (no `nextPage` key) — return items directly
- Max page depth safeguard (configurable, default 1000)

## 5. Database Models (see models.md)

Key updates from original plan:
- **Agent**: added `queues` column (ARRAY[String])
- **AgentPerformanceSnapshot**: added `checkout` (DateTime, nullable) + `queues` (ARRAY[String]) columns; indexed on `(agent_email, captured_at)`
- **AgentMetric**: unique constraint on `(session_id, agent_id)`; all metric columns have explicit defaults; ETL casts strings → int/float
- **Queue**: standalone table, auto-populated from Agent.queues arrays
- **All models**: include `raw_json` (JSONB) + `created_at`/`updated_at` timestamps

## 6. Startup Lifecycle

```python
@asynccontextmanager
async def lifespan(app):
    # 1. Create tables (or alembic upgrade)
    # 2. Run backfill (blocks until complete)
    # 3. Set backfill_complete flag
    # 4. Start APScheduler
    # 5. Yield
    # 6. Shutdown scheduler on teardown
```

## 7. Token Auto-Refresh

The Botmaker API access token is a JWT with expiration. The client decodes the JWT payload and checks the `exp` claim before every request. If the token is expired (or within 60s of expiry), it automatically calls `POST /auth/credentials` to renew:

- **Endpoint**: `https://api.botmaker.com/v2.0/auth/credentials`
- **Request body**: `{ "clientId": "...", "secretId": "...", "refreshToken": "..." }`
- **Response**: `{ "accessToken": "new.jwt", "refreshToken": "new.refresh", ... }`
- The new `accessToken` is updated in memory AND written back to `.env`
- If a 401 occurs despite a valid-looking token (e.g. revoked), the client attempts one refresh and retries the request. If the second attempt also returns 401, `BotmakerAuthError` is raised.

This means the access token in `.env` can be manually set with a fresh one at deploy time, and the system will keep it alive automatically.

### Testing the API from a browser

Mira la Documentación de Botmaker API para probar y aprender con ejemplos desde tu browser.

Cuando quieras hacer llamados a el API de Botmaker desde tus servidores, también se te solicitará autenticación usando el 'Access Token' provisto aquí. Este token es un JWT (JSON web token) y tiene expiración. Ten en cuenta que vas a necesitar renovarlo periódicamente mediante un llamado al servicio REST `refreshAPICredentials`.

```
POST https://api.botmaker.com/v2.0/auth/credentials

Generates new API credentials from the refreshToken

Request Body:
  clientId     string  required  — Client Id from Botmaker platform
  secretId     string  required  — Secret ID
  refreshToken string  required  — A JWT required

Response 200:
  accessToken  string  — The JWT token to access the API. Expiration time: 5 years.
  refreshToken string  — The JWT token to get new credentials.
  clientId     string
  secretId     string

Example curl:
curl --request POST \
  --url https://api.botmaker.com/v2.0/auth/credentials \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --header 'access-token: <refreshToken>' \
  --data '{
    "clientId": "AmericanIslands",
    "secretId": "E1COHNBWY0PZWBVR53IXKPY0ODN5MA",
    "refreshToken": "eyJhb.eyJzd.KMUFs"
  }'
```

These fields can be consulted at:
- Botmaker API section
- through api calling `GET https://api.botmaker.com/v2.0/auth/credentials`

## 8. Out of Scope
- List Sessions endpoint (increases BI data costs)
- Web UI / dashboard
- WebSocket streaming
- Multi-tenant isolation
- Alerting / notification system

## 9. Key Risks & Mitigations
| Risk | Mitigation |
|---|---|
| API rate limiting (429) | Exponential backoff with jitter |
| Deep pagination on backfill | Sliding 1-day windows, max page cap |
| AgentPerformanceSnapshot volume | Append-only per minute; flagged for retention policy |
| Numeric fields are strings in API | `int()`/`float()` casting in ETL mapper |
| Race condition backfill↔sync | `backfill_complete` gate before scheduler starts |
| DB not ready on startup | Docker healthcheck + connection retry
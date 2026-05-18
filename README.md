# Botmaker Data Orchestrator

Pipeline ETL que extrae métricas desde la API de Botmaker v2.0, las transforma y las carga en PostgreSQL para ser consumidas por Metabase u otras herramientas de analytics.

## Arquitectura

```
Botmaker API v2.0  ──►  BotmakerClient (httpx async)  ──►  ETL Mapper  ──►  PostgreSQL
                                                                               │
                                                                          Metabase
```

### Componentes principales

| Componente | Descripción |
|---|---|
| `app/clients/botmaker_client.py` | Cliente HTTP asíncrono con reconexión automática, reintentos y refresco de JWT |
| `app/services/etl_mapper.py` | Mapea los campos de la API de Botmaker al modelo de base de datos |
| `app/services/data_ingestion.py` | Operaciones upsert/insert usando `ON CONFLICT` de PostgreSQL |
| `app/tasks/sync.py` | Sincronización incremental continua cada N segundos |
| `app/tasks/scheduler.py` | Programador de tareas basado en APScheduler |
| `app/core/timestamp_manager.py` | Gestiona el timestamp de última sincronización en base de datos |

### Flujo de datos

1. El scheduler ejecuta `sync_all_endpoints()` cada 5 minutos (configurable).
2. Lee el último timestamp de sincronización desde la tabla `sync_metadata`.
3. Consulta la API de Botmaker usando ese timestamp como ventana de tiempo.
4. Transforma los datos con el ETL mapper.
5. Inserta o actualiza registros en PostgreSQL mediante upserts.
6. Guarda el timestamp actual como nueva referencia para la próxima ejecución.

Si una ejecución falla, en el próximo intervalo se retoma desde el último timestamp exitoso, cubriendo el período perdido.

## Modelo de Base de Datos

| Tabla | Descripción | Clave |
|---|---|---|
| `agents` | Agentes de Botmaker | `id` (PK) |
| `channels` | Canales de comunicación | `id` (PK) |
| `queues` | Colas extraídas de los agentes | `name` (PK) |
| `agent_metrics` | Métricas de sesión por agente | `(session_id, agent_id)` unique |
| `agent_performance_snapshots` | Instantáneas de estado de agente (serie temporal) | auto-incremental, append-only |
| `sync_metadata` | Metadatos de sincronización (timestamps) | `key` (PK) |

## Requisitos

- Docker y Docker Compose
- Credenciales de API de Botmaker (https://go.botmaker.com/#/api/)

## Configuración

### 1. Variables de entorno

```bash
cp .env.example .env
```

Editar `.env`:

| Variable | Descripción | Requerida |
|---|---|---|
| `BOTMAKER_ACCESS_TOKEN` | Token JWT de acceso | Sí |
| `CLIENT_ID` | Client ID de Botmaker (ej. `telviso`) | Sí |
| `SECRET_ID` | Secret ID de Botmaker | Sí |
| `REFRESH_TOKEN` | Token JWT de refresco | Sí |
| `DATABASE_URL` | Cadena de conexión a PostgreSQL | Sí |
| `FETCH_INTERVAL_SECONDS` | Intervalo de sincronización (default: `300`) | No |

### 2. Iniciar con Docker

```bash
docker compose up -d --build
```

Esto inicia:
- `api` — Aplicación FastAPI con el pipeline ETL + migraciones automáticas
- `db` — PostgreSQL 16
- `metabase` — Metabase para visualización de datos

Las migraciones de base de datos se ejecutan automáticamente al iniciar el contenedor.

### 3. Verificar estado

```bash
curl http://localhost:8000/health
```

## Migraciones con Alembic

El proyecto usa Alembic para gestionar cambios en el esquema de base de datos.

### Ejecutar migraciones (automático)

Al iniciar el contenedor con Docker Compose, el script `start.sh` ejecuta automáticamente:

```bash
alembic upgrade head
```

### Ejecutar migraciones (manual)

```bash
docker compose exec api poetry run alembic upgrade head
```

### Migrar a una versión específica

```bash
# Subir a una versión específica
docker compose exec api poetry run alembic upgrade 0002_remove_raw_json

# Subir un solo paso
docker compose exec api poetry run alembic upgrade +1
```

### Revertir migraciones (downgrade)

```bash
# Bajar un solo paso
docker compose exec api poetry run alembic downgrade -1

# Bajar a una versión específica
docker compose exec api poetry run alembic downgrade 0001_initial

# Bajar todo (borra todas las tablas)
docker compose exec api poetry run alembic downgrade base
```

### Ver versión actual

```bash
docker compose exec api poetry run alembic current
```

### Ver historial de migraciones

```bash
docker compose exec api poetry run alembic history
```

### Generar una nueva migración

```bash
docker compose exec api poetry run alembic revision --autogenerate -m "Descripcion del cambio"
```

**Importante:** Revisar siempre el archivo generado antes de ejecutarlo, ya que `--autogenerate` puede detectar cambios que no deseas (como columnas renombradas vs. eliminadas + creadas).

### Primera vez con una base de datos existente

Si ya tienes tablas en la base de datos pero Alembic no las reconoce:

```bash
# Verifica en qué versión está Alembic
docker compose exec api poetry run alembic current

# Si dice "base" pero las tablas existen, marca la migración inicial como aplicada
docker compose exec api poetry run alembic stamp 0001_initial

# Luego actualiza a la última versión
docker compose exec api poetry run alembic upgrade head
```

### Primera vez desde cero

```bash
# Inicia los servicios (las migraciones se ejecutan automáticamente)
docker compose up -d --build

# Verifica que esté en la última versión
docker compose exec api poetry run alembic current
# Debería mostrar: 0003_add_sync_metadata
```

## Endpoints de la API

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Health check + estado del scheduler |
| `POST` | `/backfill/trigger` | Activar backfill manual |

## Desarrollo

### Ejecutar tests

```bash
docker compose exec api poetry run pytest
```

O localmente:

```bash
poetry run pytest
```

### Estructura del proyecto

```
app/
├── main.py                        # FastAPI, lifespan, inicio
├── core/
│   ├── config.py                  # pydantic-settings (lectura de .env)
│   ├── database.py                # Engine y sesión asíncrona de SQLAlchemy
│   └── timestamp_manager.py       # Gestión de timestamps en DB
├── models/
│   ├── agent.py                   # Modelo de agentes
│   ├── channel.py                 # Modelo de canales
│   ├── queue.py                   # Modelo de colas
│   ├── agent_metric.py            # Métricas por sesión/agente
│   ├── agent_performance.py       # Instantáneas de estado de agente
│   └── sync_metadata.py           # Metadatos de sincronización
├── clients/
│   ├── botmaker_client.py         # Cliente HTTP con reintentos + auth
│   ├── exceptions.py              # Excepciones personalizadas
│   └── auth.py                    # Refresco de JWT
├── services/
│   ├── etl_mapper.py              # Mapeo API → DB
│   └── data_ingestion.py          # Upserts con ON CONFLICT
├── tasks/
│   ├── sync.py                    # Sincronización incremental
│   └── scheduler.py               # APScheduler
├── api/
│   └── routes.py                  # Endpoints REST
├── tests/                         # Tests unitarios
│   ├── test_sync_with_timestamps.py
│   ├── test_timestamp_manager.py
│   ├── test_etl_mapper.py
│   ├── test_data_ingestion.py
│   ├── test_client.py
│   └── test_auth.py
alembic/
├── versions/
│   ├── 0001_initial.py            # Creación inicial de tablas
│   ├── 0002_remove_raw_json.py    # Eliminación de columnas raw_json
│   └── 0003_add_sync_metadata.py  # Tabla de metadatos de sincronización
└── env.py                         # Configuración de entorno de Alembic
start.sh                            # Script de inicio con migraciones automáticas
docker-compose.yml                  # Configuración de servicios Docker
```

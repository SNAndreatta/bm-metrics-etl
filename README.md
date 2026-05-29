# ETL Pipeline de métricas de BotMaker

ETL pipeline que extrae métricas desde la API de Botmaker v2.0, las transforma y las carga en PostgreSQL para ser consumidas por herramientas de análisis de datos.

## Requisitos

- Docker y Docker Compose
- Credenciales de API de Botmaker <https://go.botmaker.com/#/api/>

## Configuración y ejecución

### 1. Variables de entorno

```bash
cp .env.template .env
```

Editar `.env`:

| Variable | Descripción | Requerida |
| --- | --- | --- |
| `BOTMAKER_ACCESS_TOKEN` | Token JWT de acceso | Sí |
| `CLIENT_ID` | Client ID de Botmaker (ej. `telviso`) | Sí |
| `SECRET_ID` | Secret ID de Botmaker | Sí |
| `REFRESH_TOKEN` | Token JWT de refresco | Sí |
| `DATABASE_URL` | Cadena de conexión a PostgreSQL | Sí |
| `FETCH_INTERVAL_SECONDS` | Intervalo de sincronización (default: `300`) | No |

### 2. Correr la aplicación

Se pueden configurar los puertos tanto de la API como de la base de datos PostgreSQL en el **_docker-compose.yml_**.

Para correr todo ejecuta en la terminal:

```bash
docker compose up -d --build
```

Esto inicia:
    - `api` — Aplicación FastAPI con el ETL
    - `db` — PostgreSQL 16

### 3. Verificar estado

```bash
curl http://host:puerto/health
```

## Endpoints de la API

| Método | Ruta | Descripción |
| --- | --- | --- |
| `GET` | `/health` | Health check + estado del scheduler |

## Modelo de Base de Datos

| Tabla | Descripción | Clave |
| --- | --- | --- |
| `agents` | Agentes de Botmaker | `id` (PK) |
| `channels` | Canales de comunicación | `id` (PK) |
| `queues` | Colas extraídas de los agentes (no hay un endpoint que las otorgue directamente) | `name` (PK) |
| `agent_metrics` | Métricas de sesión por agente | `(session_id, agent_id)` unique |
| `agent_performance_snapshots` | Instantáneas de estado de agente (serie temporal) | auto-incremental, append-only |
| `sync_metadata` | Metadatos de sincronización (timestamps) | `key` (PK) |

(de acá para abajo no es necesario usar ni saber nada de lo que dice, a no ser que quieran hacer cambios a la base de datos y necesiten hacer migraciones)

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

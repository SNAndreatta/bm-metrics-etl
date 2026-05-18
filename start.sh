#!/bin/sh
set -e

# Run migrations
echo "Running database migrations..."
poetry run alembic upgrade head

# Start the application
echo "Starting application server..."
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000

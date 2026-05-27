FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry==1.8.2 --no-cache-dir

COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

COPY . /app

EXPOSE 8000

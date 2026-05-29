from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    botmaker_access_token: str
    client_id: str = ""
    secret_id: str = ""
    refresh_token: str = ""
    database_url: str = "postgresql+asyncpg://botmaker:botmaker_pass@db:5432/botmaker_db"
    database_schema: str = "public"
    postgres_port: int = 5432
    metabase_port: int = 3000
    api_port: int = 8000
    fetch_interval_seconds: int = 300
    last_sync_timestamp: str | None = None
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_TELEMETRY_TOPIC: str
    KAFKA_CONSUMER_GROUP: str
    EXPORT_BATCH_TIMEOUT_MS: int = 1000
    EXPORT_BATCH_SIZE: int = 500
    CLICKHOUSE_HOST: str
    CLICKHOUSE_PORT: int
    CLICKHOUSE_DATABASE: str
    CLICKHOUSE_USER: str
    CLICKHOUSE_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

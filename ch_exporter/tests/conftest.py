import os

import pytest


os.environ.update(
    {
        "KAFKA_BOOTSTRAP_SERVERS": "localhost:9092",
        "KAFKA_TELEMETRY_TOPIC": "telemetry.events",
        "KAFKA_CONSUMER_GROUP": "exporter",
        "CLICKHOUSE_HOST": "localhost",
        "CLICKHOUSE_PORT": "8123",
        "CLICKHOUSE_DATABASE": "telemetry",
        "CLICKHOUSE_USER": "user",
        "CLICKHOUSE_PASSWORD": "password",
    }
)


@pytest.fixture
def anyio_backend():
    return "asyncio"

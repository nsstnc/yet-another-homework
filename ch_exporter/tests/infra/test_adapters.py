import json
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.domain.entities.telemetry_event import TelemetryEvent
from src.infra.clickhouse.event_repository import ClickHouseEventRepository
from src.infra.kafka import consumer
from src.infra.kafka.consumer import KafkaTelemetryConsumer, message_to_domain


def payload():
    return {
        "event_id": str(uuid4()),
        "event_type": "opened",
        "user_id": str(uuid4()),
        "session_id": None,
        "timestamp": "2026-01-01T00:00:00+00:00",
        "properties": {"page": "home"},
    }


@pytest.mark.anyio
async def test_clickhouse_repository_serializes_rows():
    client = AsyncMock()
    value = TelemetryEvent(uuid4(), "opened", uuid4(), None, datetime(2026, 1, 1, tzinfo=UTC), {"page": "home"})

    await ClickHouseEventRepository(client).save_many([value])

    args, kwargs = client.insert.await_args
    assert args == ("telemetry_events", [[value.event_id, "opened", value.user_id, None, value.timestamp, '{"page": "home"}']])
    assert kwargs["column_names"] == ["event_id", "event_type", "user_id", "session_id", "timestamp", "properties"]


def test_message_to_domain_converts_json():
    value = payload()

    event = message_to_domain(json.dumps(value).encode())

    assert str(event.event_id) == value["event_id"]
    assert event.properties == {"page": "home"}


@pytest.mark.anyio
async def test_consumer_lifecycle_batch_commit_and_iteration(monkeypatch):
    client = AsyncMock()
    monkeypatch.setattr(consumer, "AIOKafkaConsumer", Mock(return_value=client))
    value = payload()
    client.__anext__.return_value = SimpleNamespace(value=json.dumps(value).encode())
    client.getmany.return_value = {"partition": ["record"]}
    instance = KafkaTelemetryConsumer("server", "topic", "group")

    await instance.start()
    await instance.stop()
    assert instance.__aiter__() is instance
    event = await instance.__anext__()
    assert await instance.get_batch(10, 100) == {"partition": ["record"]}
    await instance.commit()

    assert event.event_type == "opened"
    client.start.assert_awaited_once()
    client.stop.assert_awaited_once()
    client.commit.assert_awaited_once()

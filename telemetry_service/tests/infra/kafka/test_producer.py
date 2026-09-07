import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.domain.entities.telemetry_event import TelemetryEvent
from src.infra.kafka.producer import KafkaEventProducer


@pytest.mark.anyio
async def test_kafka_producer_serializes_event():
    client = AsyncMock()
    event = TelemetryEvent(uuid4(), "opened", uuid4(), None, datetime(2026, 1, 1, tzinfo=UTC), {"page": "home"})

    await KafkaEventProducer(client, "events").produce(event)

    topic, payload = client.send_and_wait.await_args.args
    assert topic == "events"
    assert json.loads(payload) == {
        "event_id": str(event.event_id),
        "event_type": "opened",
        "user_id": str(event.user_id),
        "session_id": None,
        "timestamp": event.timestamp.isoformat(),
        "properties": {"page": "home"},
    }

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.api.dependencies.producer import get_event_producer
from src.api.routes import events
from src.api.schemas.event import ProduceEventRequest
from src.infra.kafka.producer import KafkaEventProducer


def test_dependency_creates_kafka_producer():
    client = object()
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(kafka_producer=client)))

    producer = get_event_producer(request)

    assert isinstance(producer, KafkaEventProducer)
    assert producer._producer is client
    assert producer._topic == "telemetry.events"


@pytest.mark.anyio
async def test_event_route_returns_accepted_event(monkeypatch):
    event = SimpleNamespace(event_id=uuid4())
    use_case = AsyncMock()
    use_case.execute.return_value = event
    monkeypatch.setattr(events, "ProduceEvent", lambda **_: use_case)
    request = ProduceEventRequest(event_type="opened", timestamp=datetime(2026, 1, 1, tzinfo=UTC))

    result = await events.produce_event(request, object())

    assert result == {"event_id": event.event_id, "status": "accepted"}
    use_case.execute.assert_awaited_once_with(
        event_type="opened", user_id=None, session_id=None, timestamp=request.timestamp, properties={}
    )


def test_event_schema_validates_type():
    with pytest.raises(Exception):
        ProduceEventRequest(event_type="")

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.app.use_cases.produce_event import ProduceEvent


@pytest.mark.anyio
async def test_produces_event_with_given_timestamp():
    producer = AsyncMock()
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)
    user_id, session_id = uuid4(), uuid4()

    event = await ProduceEvent(producer).execute("opened", user_id, session_id, timestamp, {"page": "home"})

    assert event.event_type == "opened"
    assert event.user_id == user_id
    assert event.session_id == session_id
    assert event.timestamp == timestamp
    producer.produce.assert_awaited_once_with(event)


@pytest.mark.anyio
async def test_produces_event_with_current_timestamp():
    producer = AsyncMock()

    event = await ProduceEvent(producer).execute("opened", None, None, None, {})

    assert event.timestamp.tzinfo is UTC
    assert event.properties == {}

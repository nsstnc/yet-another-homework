from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.app.use_cases.export_event import ExportTelemetryBatch, ExportTelemetryEvent
from src.domain.entities.telemetry_event import TelemetryEvent


def event():
    return TelemetryEvent(uuid4(), "opened", None, None, datetime.now(UTC), {})


@pytest.mark.anyio
async def test_export_single_event_delegates_to_repository():
    repository = AsyncMock()
    value = event()

    await ExportTelemetryEvent(repository).execute(value)

    repository.save.assert_awaited_once_with(value)


@pytest.mark.anyio
async def test_export_batch_skips_empty_and_saves_events():
    repository = AsyncMock()
    use_case = ExportTelemetryBatch(repository)
    values = [event(), event()]

    await use_case.execute([])
    await use_case.execute(values)

    repository.save_many.assert_awaited_once_with(values)

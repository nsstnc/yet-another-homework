import asyncio
import importlib
import json
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.domain.repositories.event_repository import EventRepository
from src.logging_config import JsonFormatter, configure_logging


def test_formatter_and_configuration():
    record = logging.LogRecord("exporter", logging.ERROR, "", 1, "failed", (), None)
    record.service = "exporter"
    record.request_id = "request"
    record.exc_info = (ValueError, ValueError("bad"), None)
    result = json.loads(JsonFormatter().format(record))

    assert result["service"] == "exporter"
    assert result["request_id"] == "request"
    assert "exc_info" in result
    configure_logging(logging.DEBUG)
    assert logging.getLogger().level == logging.DEBUG
    assert logging.getLogger("asyncio").level == logging.WARNING


@pytest.mark.anyio
async def test_repository_contract_default_method_raises():
    class Repository(EventRepository):
        async def save_many(self, events):
            return await super().save_many(events)

    with pytest.raises(NotImplementedError):
        await Repository().save_many([])


class StopRun(Exception):
    pass


def record_value():
    return json.dumps(
        {
            "event_id": str(uuid4()),
            "event_type": "opened",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "properties": {},
        }
    ).encode()


@pytest.mark.anyio
async def test_run_exports_records_and_closes_resources(monkeypatch):
    main = importlib.import_module("src.main")
    consumer = SimpleNamespace(
        start=AsyncMock(), stop=AsyncMock(), commit=AsyncMock(),
        get_batch=AsyncMock(side_effect=[{"partition": [SimpleNamespace(value=record_value())]}, StopRun()]),
    )
    client = AsyncMock()
    monkeypatch.setattr(main, "KafkaTelemetryConsumer", Mock(return_value=consumer))
    monkeypatch.setattr(main.clickhouse_connect, "get_async_client", AsyncMock(return_value=client))
    monkeypatch.setattr(main, "configure_logging", Mock())

    with pytest.raises(StopRun):
        await main.run()

    consumer.commit.assert_awaited_once()
    consumer.stop.assert_awaited_once()
    client.close.assert_awaited_once()


@pytest.mark.anyio
async def test_run_waits_when_batch_empty(monkeypatch):
    main = importlib.import_module("src.main")
    consumer = SimpleNamespace(start=AsyncMock(), stop=AsyncMock(), get_batch=AsyncMock(return_value={}))
    client = AsyncMock()

    async def stop_sleep(*args):
        raise StopRun()

    monkeypatch.setattr(main, "KafkaTelemetryConsumer", Mock(return_value=consumer))
    monkeypatch.setattr(main.clickhouse_connect, "get_async_client", AsyncMock(return_value=client))
    monkeypatch.setattr(main.asyncio, "sleep", stop_sleep)

    with pytest.raises(StopRun):
        await main.run()

    consumer.stop.assert_awaited_once()
    client.close.assert_awaited_once()


def test_main_runs_coroutine(monkeypatch):
    main = importlib.import_module("src.main")
    runner = Mock()
    monkeypatch.setattr(main.asyncio, "run", runner)

    main.main()

    runner.assert_called_once()
    runner.call_args.args[0].close()

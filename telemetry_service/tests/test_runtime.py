import importlib
import json
import logging
from unittest.mock import AsyncMock, Mock

import pytest

from src.domain.ports.event_producer import EventProducer
from src.logging_config import JsonFormatter, configure_logging


def test_formatter_keeps_extra_and_exception():
    record = logging.LogRecord("telemetry", logging.ERROR, "", 1, "failed", (), None)
    record.service = "telemetry"
    record.request_id = "request"
    record.exc_info = (ValueError, ValueError("bad"), None)

    result = json.loads(JsonFormatter().format(record))

    assert result["service"] == "telemetry"
    assert result["request_id"] == "request"
    assert "exception" in result


def test_configure_logging_replaces_handlers():
    root = logging.getLogger()
    root.addHandler(logging.NullHandler())

    configure_logging(logging.DEBUG)

    assert root.level == logging.DEBUG
    assert isinstance(root.handlers[0].formatter, JsonFormatter)
    assert logging.getLogger("uvicorn").propagate is True
    assert logging.getLogger("asyncio").level == logging.WARNING


@pytest.mark.anyio
async def test_lifespan_starts_and_stops_producer(monkeypatch):
    main = importlib.import_module("src.main")
    producer = AsyncMock()
    constructor = Mock(return_value=producer)
    monkeypatch.setattr(main, "AIOKafkaProducer", constructor)
    app = Mock()
    app.state = Mock()

    async with main.lifespan(app):
        assert app.state.kafka_producer is producer

    producer.start.assert_awaited_once()
    producer.stop.assert_awaited_once()


def test_app_and_main(monkeypatch):
    main = importlib.import_module("src.main")
    app = main.create_app()
    configure, run = Mock(), Mock()
    monkeypatch.setattr(main, "configure_logging", configure)
    monkeypatch.setattr(main.uvicorn, "run", run)

    main.main()

    assert app.title == "Telemetry Service"
    assert app.router.routes
    run.assert_called_once_with("src.main:app", host="0.0.0.0", port=8001, reload=True, log_config=None)


@pytest.mark.anyio
async def test_producer_contract_default_method_raises():
    class Producer(EventProducer):
        async def produce(self, event):
            return await super().produce(event)

    with pytest.raises(NotImplementedError):
        await Producer().produce(object())

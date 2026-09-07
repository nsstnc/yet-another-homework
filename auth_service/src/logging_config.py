from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created,
                tz=timezone.utc,
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        service = getattr(record, "service", None)
        if service is not None:
            log_record["service"] = service

        skip_keys = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "message",
            "color_message",
        }

        for key, value in record.__dict__.items():
            if key in skip_keys or key in log_record:
                continue
            log_record[key] = value

        if record.exc_info:
            log_record["exception"] = self.formatException(
                record.exc_info
            )

        return json.dumps(
            log_record,
            ensure_ascii=False,
            default=str,
        )


_THIRD_PARTY_QUIET: tuple[str, ...] = (
    "asyncio",
    "concurrent.futures",
)


def configure_logging(
        level: int = logging.INFO,
) -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root_logger.addHandler(handler)

    for name in (
            "uvicorn",
            "uvicorn.error",
            "uvicorn.access",
    ):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True

    for name in _THIRD_PARTY_QUIET:
        logging.getLogger(name).setLevel(logging.WARNING)

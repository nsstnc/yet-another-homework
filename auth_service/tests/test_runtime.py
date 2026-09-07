import importlib
import json
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import APIRouter

from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.user_session_repository import UserSessionRepository
from src.logging_config import JsonFormatter, configure_logging


def test_formatter_includes_service_extra_and_exception():
    formatter = JsonFormatter()
    record = logging.LogRecord("name", logging.ERROR, "", 1, "message %s", ("text",), None)
    record.service = "auth"
    record.request_id = "request"
    record.exc_info = (ValueError, ValueError("bad"), None)

    payload = json.loads(formatter.format(record))

    assert payload["service"] == "auth"
    assert payload["request_id"] == "request"
    assert "exception" in payload


def test_configure_logging_replaces_handlers_and_quiets_libraries():
    root = logging.getLogger()
    old_handler = logging.NullHandler()
    root.addHandler(old_handler)

    configure_logging(logging.DEBUG)

    assert root.level == logging.DEBUG
    assert old_handler not in root.handlers
    assert isinstance(root.handlers[0].formatter, JsonFormatter)
    assert logging.getLogger("asyncio").level == logging.WARNING


def test_create_app_includes_auth_routes():
    main = importlib.import_module("src.main")
    app = main.create_app()

    assert app.title == "Auth Service"
    assert app.router.routes


def test_main_configures_server(monkeypatch):
    main = importlib.import_module("src.main")
    configure, run = Mock(), Mock()
    monkeypatch.setattr(main, "configure_logging", configure)
    monkeypatch.setattr(main.uvicorn, "run", run)

    main.main()

    configure.assert_called_once()
    run.assert_called_once_with("src.main:app", host="0.0.0.0", port=8000, reload=True, log_config=None)


@pytest.mark.anyio
async def test_database_session_yields_and_closes(monkeypatch):
    engine = importlib.import_module("src.infra.database.engine")
    session = object()

    class Factory:
        async def __aenter__(self):
            return session

        async def __aexit__(self, *args):
            return None

    monkeypatch.setattr(engine, "async_session_factory", lambda: Factory())
    generator = engine.get_db_session()

    assert await anext(generator) is session
    with pytest.raises(StopAsyncIteration):
        await anext(generator)


@pytest.mark.anyio
async def test_repository_contract_default_methods_raise():
    class Users(UserRepository):
        async def get_by_email(self, email):
            return await super().get_by_email(email)

        async def add(self, user):
            return await super().add(user)

    class Sessions(UserSessionRepository):
        async def get_by_refresh_token_hash(self, value):
            return await super().get_by_refresh_token_hash(value)

        async def add(self, value):
            return await super().add(value)

        async def revoke_session(self, value):
            return await super().revoke_session(value)

    users, sessions = Users(), Sessions()
    with pytest.raises(NotImplementedError):
        await users.get_by_email("email")
    with pytest.raises(NotImplementedError):
        await users.add(object())
    with pytest.raises(NotImplementedError):
        await sessions.get_by_refresh_token_hash("token")
    with pytest.raises(NotImplementedError):
        await sessions.add(object())
    with pytest.raises(NotImplementedError):
        await sessions.revoke_session(object())


def test_auth_router_is_router():
    module = importlib.import_module("src.api.routes.auth.router")
    assert isinstance(module.router, APIRouter)


def test_route_discovery_router_is_router():
    module = importlib.import_module("src.api.routes.router")
    assert isinstance(module.router, APIRouter)

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.app.use_cases.login_user import InvalidCredentialsError, LoginUser, UserDoesNotExists


@pytest.mark.anyio
async def test_login_creates_session_and_returns_tokens(monkeypatch):
    user = SimpleNamespace(id=uuid4(), password_hash="stored")
    users, sessions = AsyncMock(), AsyncMock()
    users.get_by_email.return_value = user
    monkeypatch.setattr("src.app.use_cases.login_user.Security.verify", lambda *_: True)
    monkeypatch.setattr("src.app.use_cases.login_user.Security.generate_refresh_token", lambda: "refresh")
    monkeypatch.setattr("src.app.use_cases.login_user.Security.hash_refresh_token", lambda _: "hashed")
    monkeypatch.setattr("src.app.use_cases.login_user.Security.generate_access_token", lambda *_: "access")

    result = await LoginUser(users, sessions).execute("user@example.com", "secret")

    assert result.access_token == "access"
    assert result.refresh_token == "refresh"
    session = sessions.add.await_args.args[0]
    assert session.user_id == user.id
    assert session.refresh_token_hash == "hashed"
    assert session.created_at <= datetime.now(UTC)


@pytest.mark.anyio
async def test_login_rejects_unknown_user():
    users, sessions = AsyncMock(), AsyncMock()
    users.get_by_email.return_value = None

    with pytest.raises(UserDoesNotExists):
        await LoginUser(users, sessions).execute("user@example.com", "secret")


@pytest.mark.anyio
async def test_login_rejects_bad_password(monkeypatch):
    users, sessions = AsyncMock(), AsyncMock()
    users.get_by_email.return_value = SimpleNamespace(password_hash="stored")
    monkeypatch.setattr("src.app.use_cases.login_user.Security.verify", lambda *_: False)

    with pytest.raises(InvalidCredentialsError):
        await LoginUser(users, sessions).execute("user@example.com", "bad")

    sessions.add.assert_not_awaited()

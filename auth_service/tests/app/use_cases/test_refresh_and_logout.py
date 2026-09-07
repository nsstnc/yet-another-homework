from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.app.use_cases.logout_user import InvalidSessionError, LogoutUser
from src.app.use_cases.refresh_token import RefreshToken, SessionDoesNotExists, SessionHasExpired, SessionWasRevoked


def session(**values):
    defaults = dict(id=uuid4(), user_id=uuid4(), expires_at=datetime.now(UTC) + timedelta(days=1), revoked_at=None)
    defaults.update(values)
    return SimpleNamespace(**defaults)


@pytest.mark.anyio
async def test_refresh_rotates_session(monkeypatch):
    sessions = AsyncMock()
    old = session()
    sessions.get_by_refresh_token_hash.return_value = old
    monkeypatch.setattr("src.app.use_cases.refresh_token.Security.hash_refresh_token", lambda value: f"hash:{value}")
    monkeypatch.setattr("src.app.use_cases.refresh_token.Security.generate_refresh_token", lambda: "new")
    monkeypatch.setattr("src.app.use_cases.refresh_token.Security.generate_access_token", lambda *_: "access")

    result = await RefreshToken(sessions).execute("old")

    assert result.access_token == "access"
    assert result.refresh_token == "new"
    assert sessions.add.await_args.args[0].refresh_token_hash == "hash:new"
    sessions.revoke_session.assert_awaited_once_with(old.id)


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("value", "error"),
    [
        (None, SessionDoesNotExists),
        (session(expires_at=datetime.now(UTC) - timedelta(seconds=1)), SessionHasExpired),
        (session(revoked_at=datetime.now(UTC)), SessionWasRevoked),
    ],
)
async def test_refresh_rejects_invalid_session(monkeypatch, value, error):
    sessions = AsyncMock()
    sessions.get_by_refresh_token_hash.return_value = value
    monkeypatch.setattr("src.app.use_cases.refresh_token.Security.hash_refresh_token", lambda _: "hash")

    with pytest.raises(error):
        await RefreshToken(sessions).execute("token")

    sessions.add.assert_not_awaited()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "value",
    [None, session(revoked_at=datetime.now(UTC)), session(expires_at=datetime.now(UTC) - timedelta(seconds=1))],
)
async def test_logout_rejects_invalid_session(monkeypatch, value):
    sessions = AsyncMock()
    sessions.get_by_refresh_token_hash.return_value = value
    monkeypatch.setattr("src.app.use_cases.logout_user.Security.hash_refresh_token", lambda _: "hash")

    with pytest.raises(InvalidSessionError):
        await LogoutUser(sessions).execute("token")


@pytest.mark.anyio
async def test_logout_revokes_valid_session(monkeypatch):
    sessions = AsyncMock()
    active = session()
    sessions.get_by_refresh_token_hash.return_value = active
    monkeypatch.setattr("src.app.use_cases.logout_user.Security.hash_refresh_token", lambda _: "hash")

    assert await LogoutUser(sessions).execute("token") is None
    sessions.revoke_session.assert_awaited_once_with(active.id)

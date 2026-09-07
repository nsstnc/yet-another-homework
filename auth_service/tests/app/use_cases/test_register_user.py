from unittest.mock import AsyncMock

import pytest

from src.app.use_cases.register_user import RegisterUser, UserAlreadyExistsError


@pytest.mark.anyio
async def test_registers_new_active_user(monkeypatch):
    users = AsyncMock()
    users.get_by_email.return_value = None
    monkeypatch.setattr("src.app.use_cases.register_user.Security.hash", lambda value: f"hash:{value}")

    user = await RegisterUser(users).execute("user@example.com", "secret")

    assert user.email == "user@example.com"
    assert user.password_hash == "hash:secret"
    assert user.is_active is True
    assert user.created_at == user.updated_at
    users.add.assert_awaited_once_with(user)


@pytest.mark.anyio
async def test_register_rejects_existing_email():
    users = AsyncMock()
    users.get_by_email.return_value = object()

    with pytest.raises(UserAlreadyExistsError):
        await RegisterUser(users).execute("user@example.com", "secret")

    users.add.assert_not_awaited()

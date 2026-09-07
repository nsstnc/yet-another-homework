from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.api.routes.auth import login, logout, refresh, register
from src.api.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest


@pytest.mark.anyio
async def test_register_route_returns_public_user(monkeypatch):
    use_case = AsyncMock()
    use_case.execute.return_value = SimpleNamespace(id="id", email="user@example.com")
    monkeypatch.setattr(register, "SqlAlchemyUserRepository", lambda _: object())
    monkeypatch.setattr(register, "RegisterUser", lambda **_: use_case)

    result = await register.register(RegisterRequest(email="user@example.com", password="secret"), object())

    assert result == {"id": "id", "email": "user@example.com"}
    use_case.execute.assert_awaited_once_with(email="user@example.com", password="secret")


@pytest.mark.anyio
async def test_login_route_returns_tokens(monkeypatch):
    use_case = AsyncMock()
    use_case.execute.return_value = "tokens"
    monkeypatch.setattr(login, "SqlAlchemyUserRepository", lambda _: object())
    monkeypatch.setattr(login, "SqlAlchemyUserSessionRepository", lambda _: object())
    monkeypatch.setattr(login, "LoginUser", lambda **_: use_case)

    assert await login.login(LoginRequest(email="user@example.com", password="secret"), object()) == "tokens"


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("module", "handler", "request_type", "use_case_name"),
    [
        (refresh, "refresh", RefreshRequest, "RefreshToken"),
        (logout, "logout", LogoutRequest, "LogoutUser"),
    ],
)
async def test_token_routes_delegate_to_use_case(monkeypatch, module, handler, request_type, use_case_name):
    use_case = AsyncMock()
    use_case.execute.return_value = None
    monkeypatch.setattr(module, "SqlAlchemyUserSessionRepository", lambda _: object())
    monkeypatch.setattr(module, use_case_name, lambda **_: use_case)

    result = await getattr(module, handler)(request_type(refresh_token="token"), object())

    assert result is None
    use_case.execute.assert_awaited_once_with("token")

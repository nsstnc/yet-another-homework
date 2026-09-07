import hashlib
from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from jose import JWTError

from src.api.dependencies.security import Security, Tokens


def test_security_hash_verify_and_refresh_token(monkeypatch):
    context = Mock()
    context.hash.return_value = "hashed"
    context.verify.return_value = True
    monkeypatch.setattr("src.api.dependencies.security.pwd_context", context)

    assert Security.hash("secret") == "hashed"
    assert Security.verify("secret", "hashed") is True
    token = Security.generate_refresh_token()
    assert len(token) >= 48
    assert Security.hash_refresh_token("token") == hashlib.sha256(b"token").hexdigest()


def test_access_token_round_trip():
    token = Security.generate_access_token("user", "session")
    payload = Security.decode_access_token(token)

    assert payload["sub"] == "user"
    assert payload["sid"] == "session"
    assert payload["type"] == "access"
    assert datetime.fromtimestamp(payload["exp"], UTC) > datetime.now(UTC)


def test_access_token_rejects_wrong_type(monkeypatch):
    monkeypatch.setattr("src.api.dependencies.security.jwt.decode", lambda *args, **kwargs: {"type": "refresh"})

    with pytest.raises(JWTError, match="Invalid token type"):
        Security.decode_access_token("token")


def test_tokens_default_type():
    assert Tokens("access", "refresh").token_type == "bearer"

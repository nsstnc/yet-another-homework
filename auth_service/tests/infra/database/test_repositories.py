from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.domain.entities.user import User
from src.domain.entities.user_session import UserSession
from src.infra.database.repositories.user_repository import SqlAlchemyUserRepository
from src.infra.database.repositories.user_session_repository import SqlAlchemyUserSessionRepository


def user():
    now = datetime.now(UTC)
    return User(uuid4(), "user@example.com", "hash", True, now, now)


def session():
    now = datetime.now(UTC)
    return UserSession(uuid4(), uuid4(), "hash", now, now)


@pytest.mark.anyio
async def test_user_repository_returns_none_when_not_found():
    db = SimpleNamespace(execute=AsyncMock(), add=Mock(), commit=AsyncMock())
    result = Mock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result

    assert await SqlAlchemyUserRepository(db).get_by_email("none@example.com") is None


@pytest.mark.anyio
async def test_user_repository_maps_model_and_adds_entity():
    entity = user()
    db = SimpleNamespace(execute=AsyncMock(), add=Mock(), commit=AsyncMock())
    model = SimpleNamespace(**entity.__dict__)
    result = Mock()
    result.scalar_one_or_none.return_value = model
    db.execute.return_value = result
    repository = SqlAlchemyUserRepository(db)

    found = await repository.get_by_email(entity.email)
    await repository.add(entity)

    assert found == entity
    db.add.assert_called_once()
    db.commit.assert_awaited_once()


@pytest.mark.anyio
async def test_session_repository_handles_read_write_and_revoke():
    entity = session()
    db = SimpleNamespace(execute=AsyncMock(), add=Mock(), commit=AsyncMock())
    model = SimpleNamespace(**entity.__dict__)
    found_result, revoke_result, empty_result = Mock(), Mock(), Mock()
    found_result.scalar_one_or_none.return_value = model
    revoke_result.scalar_one_or_none.return_value = entity.id
    empty_result.scalar_one_or_none.return_value = None
    db.execute.side_effect = [found_result, revoke_result, empty_result]
    repository = SqlAlchemyUserSessionRepository(db)

    assert await repository.get_by_refresh_token_hash("hash") == entity
    await repository.add(entity)
    assert await repository.revoke_session(entity.id) is True
    assert await repository.revoke_session(entity.id) is False
    assert db.commit.await_count == 3


@pytest.mark.anyio
async def test_session_repository_returns_none_when_not_found():
    db = SimpleNamespace(execute=AsyncMock(), add=Mock(), commit=AsyncMock())
    result = Mock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result

    assert await SqlAlchemyUserSessionRepository(db).get_by_refresh_token_hash("missing") is None


def test_session_entity_knows_revocation():
    entity = session()
    assert entity.is_revoked is False
    entity.revoked_at = datetime.now(UTC)
    assert entity.is_revoked is True

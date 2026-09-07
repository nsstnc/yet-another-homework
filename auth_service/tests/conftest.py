import os

import pytest


os.environ.update(
    {
        "database_url": "postgresql+asyncpg://user:password@localhost/test",
        "SECRET_KEY": "test-secret",
    }
)


@pytest.fixture
def anyio_backend():
    return "asyncio"

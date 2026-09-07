import os

import pytest


os.environ["KAFKA_BOOTSTRAP_SERVERS"] = "localhost:9092"


@pytest.fixture
def anyio_backend():
    return "asyncio"

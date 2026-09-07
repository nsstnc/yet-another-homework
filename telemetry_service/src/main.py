import logging
import uvicorn
from contextlib import asynccontextmanager
from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from src.config import settings
from src.logging_config import configure_logging
from src.api.routes.events import router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    )

    await producer.start()

    app.state.kafka_producer = producer

    try:
        yield
    finally:
        await producer.stop()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Telemetry Service",
        lifespan=lifespan,
    )

    app.include_router(router)

    return app


app = create_app()


def main() -> None:
    configure_logging()
    logger.info("Starting telemetry_service...")

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )


if __name__ == "__main__":
    main()

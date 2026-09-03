import asyncio
import logging

from src.logging_config import configure_logging

logger = logging.getLogger(__name__)


async def run_app():
    logger.info("Starting ch_exporter...")


def main() -> None:
    configure_logging()

    asyncio.run(run_app())


if __name__ == "__main__":
    main()

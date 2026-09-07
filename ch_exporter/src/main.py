import asyncio
import logging
import clickhouse_connect

from src.app.use_cases.export_event import ExportTelemetryBatch
from src.config import settings
from src.infra.clickhouse.event_repository import (
    ClickHouseEventRepository,
)
from src.infra.kafka.consumer import KafkaTelemetryConsumer, message_to_domain
from src.logging_config import configure_logging

logger = logging.getLogger(__name__)


async def run() -> None:
    configure_logging()
    logger.info("Starting ch_exporter")

    consumer = KafkaTelemetryConsumer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        topic=settings.KAFKA_TELEMETRY_TOPIC,
        group_id=settings.KAFKA_CONSUMER_GROUP,
    )

    clickhouse_client = await clickhouse_connect.get_async_client(
        host=settings.CLICKHOUSE_HOST,
        port=settings.CLICKHOUSE_PORT,
        username=settings.CLICKHOUSE_USER,
        password=settings.CLICKHOUSE_PASSWORD,
        database=settings.CLICKHOUSE_DATABASE,
    )

    repository = ClickHouseEventRepository(
        clickhouse_client
    )

    use_case = ExportTelemetryBatch(repository)

    await consumer.start()

    try:
        while True:
            records = await consumer.get_batch(
                max_records=settings.EXPORT_BATCH_SIZE,
                timeout_ms=settings.EXPORT_BATCH_TIMEOUT_MS,
            )

            events = []

            for partition_records in records.values():
                for record in partition_records:
                    event = message_to_domain(
                        record.value
                    )
                    events.append(event)

            if not events:
                logger.info("Not found new Events, retry after 5 sec")
                await asyncio.sleep(5)
                continue

            logger.info(f"Inserting {len(events)} events into ClickHouse")
            await use_case.execute(events)

            await consumer.commit()

    finally:
        await consumer.stop()
        await clickhouse_client.close()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()

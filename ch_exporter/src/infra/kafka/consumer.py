import json

from aiokafka import AIOKafkaConsumer

from src.domain.entities.telemetry_event import TelemetryEvent
from src.infra.kafka.schemas import TelemetryEventMessage


class KafkaTelemetryConsumer:
    def __init__(
            self,
            bootstrap_servers: str,
            topic: str,
            group_id: str,
    ) -> None:
        self._consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
        )

    async def start(self) -> None:
        await self._consumer.start()

    async def stop(self) -> None:
        await self._consumer.stop()

    def __aiter__(self):
        return self

    async def __anext__(self) -> TelemetryEvent:
        kafka_message = await self._consumer.__anext__()

        message = TelemetryEventMessage.model_validate_json(
            kafka_message.value
        )

        event = TelemetryEvent(
            event_id=message.event_id,
            event_type=message.event_type,
            user_id=message.user_id,
            session_id=message.session_id,
            timestamp=message.timestamp,
            properties=message.properties,
        )

        return event

    async def get_batch(
            self,
            max_records: int,
            timeout_ms: int,
    ):
        return await self._consumer.getmany(
            timeout_ms=timeout_ms,
            max_records=max_records,
        )

    async def commit(self) -> None:
        await self._consumer.commit()


def message_to_domain(
        value: bytes,
) -> TelemetryEvent:
    message = TelemetryEventMessage.model_validate_json(
        value
    )

    return TelemetryEvent(
        event_id=message.event_id,
        event_type=message.event_type,
        user_id=message.user_id,
        session_id=message.session_id,
        timestamp=message.timestamp,
        properties=message.properties,
    )

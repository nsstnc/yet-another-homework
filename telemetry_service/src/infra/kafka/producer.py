import json

from aiokafka import AIOKafkaProducer

from src.domain.entities.telemetry_event import TelemetryEvent
from src.domain.ports.event_producer import EventProducer


class KafkaEventProducer(EventProducer):
    def __init__(
            self,
            producer: AIOKafkaProducer,
            topic: str,
    ) -> None:
        self._producer = producer
        self._topic = topic

    async def produce(self, event: TelemetryEvent) -> None:
        payload = {
            "event_id": str(event.event_id),
            "event_type": event.event_type,
            "user_id": str(event.user_id) if event.user_id else None,
            "session_id": str(event.session_id) if event.session_id else None,
            "timestamp": event.timestamp.isoformat(),
            "properties": event.properties,
        }

        await self._producer.send_and_wait(
            self._topic,
            json.dumps(payload).encode(),
        )
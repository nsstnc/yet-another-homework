from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.domain.entities.telemetry_event import TelemetryEvent
from src.domain.ports.event_producer import EventProducer


class ProduceEvent:
    def __init__(self, producer: EventProducer) -> None:
        self._producer = producer

    async def execute(
            self,
            event_type: str,
            user_id: UUID | None,
            session_id: UUID | None,
            timestamp: datetime | None,
            properties: dict,
    ) -> TelemetryEvent:
        event = TelemetryEvent(
            event_id=uuid4(),
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            timestamp=timestamp or datetime.now(UTC),
            properties=properties,
        )

        await self._producer.produce(event)

        return event

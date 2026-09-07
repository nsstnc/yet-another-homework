from src.domain.entities.telemetry_event import TelemetryEvent
from src.domain.repositories.event_repository import EventRepository


class ExportTelemetryEvent:
    def __init__(self, repository: EventRepository) -> None:
        self._repository = repository

    async def execute(self, event: TelemetryEvent) -> None:
        await self._repository.save(event)


class ExportTelemetryBatch:
    def __init__(
            self,
            repository: EventRepository,
    ) -> None:
        self._repository = repository

    async def execute(
            self,
            events: list[TelemetryEvent],
    ) -> None:
        if not events:
            return

        await self._repository.save_many(events)

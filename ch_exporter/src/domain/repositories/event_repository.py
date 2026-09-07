from abc import ABC, abstractmethod

from src.domain.entities.telemetry_event import TelemetryEvent


class EventRepository(ABC):
    @abstractmethod
    async def save_many(
            self,
            events: list[TelemetryEvent],
    ) -> None:
        raise NotImplementedError
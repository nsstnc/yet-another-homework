from abc import ABC, abstractmethod

from src.domain.entities.telemetry_event import TelemetryEvent


class EventProducer(ABC):
    @abstractmethod
    async def produce(self, event: TelemetryEvent) -> None:
        raise NotImplementedError

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class TelemetryEvent:
    event_id: UUID
    event_type: str
    user_id: UUID | None
    session_id: UUID | None
    timestamp: datetime
    properties: dict

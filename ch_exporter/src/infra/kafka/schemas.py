from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TelemetryEventMessage(BaseModel):
    event_id: UUID
    event_type: str
    user_id: UUID | None = None
    session_id: UUID | None = None
    timestamp: datetime
    properties: dict = Field(default_factory=dict)
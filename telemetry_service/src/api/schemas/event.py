from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProduceEventRequest(BaseModel):
    event_type: str = Field(min_length=1, max_length=100)
    user_id: UUID | None = None
    session_id: UUID | None = None
    timestamp: datetime | None = None
    properties: dict = Field(default_factory=dict)
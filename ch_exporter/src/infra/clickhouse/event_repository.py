import json
import logging

from clickhouse_connect.driver.asyncclient import AsyncClient

from src.domain.entities.telemetry_event import TelemetryEvent
from src.domain.repositories.event_repository import EventRepository


logger = logging.getLogger(__name__)

class ClickHouseEventRepository(EventRepository):
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def save_many(
            self,
            events: list[TelemetryEvent],
    ) -> None:
        rows = [
            [
                event.event_id,
                event.event_type,
                event.user_id,
                event.session_id,
                event.timestamp,
                json.dumps(event.properties),
            ]
            for event in events
        ]

        await self._client.insert(
            "telemetry_events",
            rows,
            column_names=[
                "event_id",
                "event_type",
                "user_id",
                "session_id",
                "timestamp",
                "properties",
            ],
        )

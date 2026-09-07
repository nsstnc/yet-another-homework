from fastapi import APIRouter, Depends, status

from src.api.schemas.event import ProduceEventRequest
from src.app.use_cases.produce_event import ProduceEvent
from src.api.dependencies.producer import get_event_producer
from src.infra.kafka.producer import KafkaEventProducer

router = APIRouter(
    prefix="/events",
    tags=["Telemetry"],
)


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
)
async def produce_event(
        request: ProduceEventRequest,
        event_producer: KafkaEventProducer = Depends(get_event_producer),
):
    use_case = ProduceEvent(producer=event_producer)

    event = await use_case.execute(
        event_type=request.event_type,
        user_id=request.user_id,
        session_id=request.session_id,
        timestamp=request.timestamp,
        properties=request.properties,
    )

    return {
        "event_id": event.event_id,
        "status": "accepted",
    }
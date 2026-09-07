from fastapi import Request

from src.infra.kafka.producer import KafkaEventProducer


def get_event_producer(
        request: Request,
) -> KafkaEventProducer:
    return KafkaEventProducer(
        producer=request.app.state.kafka_producer,
        topic="telemetry.events",
    )
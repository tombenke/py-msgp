"""Test the rpc module"""

import asyncio
from loguru import logger
from oti import OTI, OTIConfig, ExporterConfig, SamplingConfig
from nats_messenger.messenger import Messenger
from mpa import MessageConsumerActor
from mpa.examples.config import (
    URL,
    CONSUMER_MPA_CLIENT_ID,
    PROCESSOR_OUTBOUND_TOPIC,
)


async def client():
    """Start an MPAProducer"""

    # Configure the OTEL SDK
    oti = OTI(
        OTIConfig(
            service_name="mpa_consumer",
            service_namespace="examples",
            service_instance_id="mpa_cons_0",
            service_version="v1.0.0",
            exporter_config=ExporterConfig(exporter_type="OTLPGRPC"),
            # exporter_config=ExporterConfig(exporter_type="STDOUT"),
            sampling_config=SamplingConfig(trace_sampling_type="ALWAYS_ON"),
        )
    )

    logger.debug("Setup the consumer actor")
    actor_function_called = asyncio.Future()

    async def actor_function(payload: bytes, headers: dict) -> tuple[bytes, dict]:
        actor_function_response = b"actor function response..."
        nonlocal actor_function_called
        logger.debug(
            f"Consumer actor_function is called with message: '{payload}' with headers: {headers}"
        )
        actor_function_called.set_result(None)
        return actor_function_response, headers

    consumer_actor = MessageConsumerActor(
        Messenger(URL, logger, name=CONSUMER_MPA_CLIENT_ID),
        PROCESSOR_OUTBOUND_TOPIC,
        actor_function,
        durable=False,
    )
    await consumer_actor.open()
    await asyncio.wait_for(actor_function_called, 1000)

    # Shut down the consumer actor
    await consumer_actor.close()

    # Shut down the OTEL SDK
    oti.shutdown()


if __name__ == "__main__":
    asyncio.run(client())

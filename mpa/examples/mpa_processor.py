"""Test the rpc module"""

import asyncio
from loguru import logger
from oti import OTI, OTIConfig, ExporterConfig, SamplingConfig
from nats_messenger.messenger import Messenger
from mpa import MessageProcessorActor
from mpa.examples.config import (
    URL,
    PROCESSOR_MPA_CLIENT_ID,
    PROCESSOR_INBOUND_TOPIC,
    PROCESSOR_OUTBOUND_TOPIC,
)


async def client():
    """Start an MPAProducer"""

    # Configure the OTEL SDK
    oti = OTI(
        OTIConfig(
            service_name="mpa_processor",
            service_namespace="examples",
            service_instance_id="mpa_proc_0",
            service_version="v1.0.0",
            exporter_config=ExporterConfig(exporter_type="OTELGRPC"),
            # exporter_config=ExporterConfig(exporter_type="STDOUT"),
            sampling_config=SamplingConfig(trace_sampling_type="ALWAYS"),
        )
    )

    logger.debug("Setup the processor actor")
    actor_function_called = asyncio.Future()

    async def actor_function(payload: bytes, headers: dict) -> bytes:
        actor_function_response = b"actor function response..."
        nonlocal actor_function_called
        logger.debug(
            f"Processor actor_function is called with message: '{payload}' with headers: {headers}"
        )
        actor_function_called.set_result(None)
        return actor_function_response

    processor_actor = MessageProcessorActor(
        Messenger(URL, logger, name=PROCESSOR_MPA_CLIENT_ID),
        PROCESSOR_INBOUND_TOPIC,
        PROCESSOR_OUTBOUND_TOPIC,
        actor_function,
        durable_in=False,
        durable_out=False,
    )
    await processor_actor.open()

    logger.debug("Wait for actor function callback and consumer callback")
    await asyncio.wait_for(actor_function_called, 1000)

    # Shut down the processor actor
    await processor_actor.close()

    # Shut down the OTEL SDK
    oti.shutdown()


if __name__ == "__main__":
    asyncio.run(client())

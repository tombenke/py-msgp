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
            exporter_config=ExporterConfig(exporter_type="OTLPGRPC"),
            # exporter_config=ExporterConfig(exporter_type="STDOUT"),
            sampling_config=SamplingConfig(trace_sampling_type="ALWAYS_ON"),
        )
    )

    logger.debug("Setup the processor actor")
    actor_function_called = asyncio.Future()

    async def actor_function(payload: bytes, headers: dict) -> tuple[bytes, dict]:
        """
        MPA processor's actor function, that receives a plain text content payload, and forwards an XML format response payload.
        The new payload includes the original payload, and the original `content-type` header replaced with `text/xml` before forwarding.
        """
        actor_function_response = f'<?xml version="1.0" encoding="UTF-8" standalone="yes" ?><text>{payload.decode()}</text>'.encode()
        headers["content-type"] = "text/xml"
        nonlocal actor_function_called
        logger.debug(
            f"Processor actor_function is called with message: '{payload}' with headers: {headers}"
        )
        actor_function_called.set_result(None)
        return actor_function_response, headers

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

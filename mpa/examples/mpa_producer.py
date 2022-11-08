"""Test the rpc module"""

import asyncio
from loguru import logger
from oti import OTI, OTIConfig, ExporterConfig, SamplingConfig
from nats_messenger.messenger import Messenger
from mpa import MessageProducerActor
from mpa.examples.config import (
    URL,
    PRODUCER_MPA_CLIENT_ID,
    PROCESSOR_INBOUND_TOPIC,
    TEST_PAYLOAD,
    TEST_HEADERS,
)


async def client():
    """Start an MPAProducer"""

    # Configure the OTEL SDK
    oti = OTI(
        OTIConfig(
            service_name="mpa_producer",
            service_namespace="examples",
            service_instance_id="mpa_prod_0",
            service_version="v1.0.0",
            exporter_config=ExporterConfig(exporter_type="OTLPGRPC"),
            # exporter_config=ExporterConfig(exporter_type="STDOUT"),
            sampling_config=SamplingConfig(trace_sampling_type="ALWAYS_ON"),
        )
    )

    logger.debug("Setup the producer actor")
    producer_actor = MessageProducerActor(
        Messenger(URL, logger, name=PRODUCER_MPA_CLIENT_ID),
        PROCESSOR_INBOUND_TOPIC,
        durable=False,
    )
    await producer_actor.open()

    logger.debug("Produce something")
    await producer_actor.next(TEST_PAYLOAD, headers=TEST_HEADERS)

    # Shut down the producer actor
    await producer_actor.close()

    # Shut down the OTEL SDK
    oti.shutdown()


if __name__ == "__main__":
    asyncio.run(client())

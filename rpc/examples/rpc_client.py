"""An example for the RPCClient component of the RPC module including tracing with Open Telemetry"""

import asyncio
from loguru import logger
from oti import OTI, OTIConfig, ExporterConfig, SamplingConfig
from rpc import RPCClient
from rpc.examples.config import (
    URL,
    RPC_CLIENT_ID,
    TEST_TOPIC,
    TEST_PAYLOAD,
    TEST_HEADERS,
)
from nats_messenger.messenger import Messenger


async def client():
    """
    Run RPCClient with OTEL instrumentation.

    This function demonstrates how to instrument Open Telementry,
    then create an instance of the client component of the RPC module,
    and make a call to the RPC server.
    """

    # Configure the OTEL SDK
    oti = OTI(
        OTIConfig(
            service_name="rpc_client",
            service_namespace="examples",
            service_instance_id="rpcc_0",
            service_version="v1.0.0",
            exporter_config=ExporterConfig(exporter_type="OTLPGRPC"),
            # exporter_config=ExporterConfig(exporter_type="STDOUT"),
            sampling_config=SamplingConfig(trace_sampling_type="ALWAYS_ON"),
        )
    )

    # Setup the client
    rpc_client = RPCClient(Messenger(URL, logger, name=RPC_CLIENT_ID))
    await rpc_client.open()

    # Call the server via the client
    logger.debug("Use client.call()")
    response, response_headers = await rpc_client.call(
        TEST_TOPIC, TEST_PAYLOAD, 1.0, headers=TEST_HEADERS
    )

    # Wait for service function callback
    logger.debug(
        f"Results of service function callback: payload: {response}, headers: {response_headers}"
    )

    # Shut down the server and the client
    logger.debug("Close RPC client")
    await rpc_client.close()

    # Shut down the OTEL SDK
    oti.shutdown()


if __name__ == "__main__":
    asyncio.run(client())

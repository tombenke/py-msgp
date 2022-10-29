"""Test the rpc module"""

import asyncio
from loguru import logger
from oti import OTI, OTIConfig, ExporterConfig, SamplingConfig
from nats_messenger.messenger import Messenger
from rpc import RPCServer
from rpc.examples.config import (
    URL,
    RPC_SERVER_ID,
    TEST_TOPIC,
)


async def server():
    """Start an RPCServer"""

    # Configure the OTEL SDK
    oti = OTI(
        OTIConfig(
            service_name="rpc_server",
            service_namespace="examples",
            service_instance_id="rpcs_0",
            service_version="v1.0.0",
            exporter_config=ExporterConfig(exporter_type="OTELGRPC"),
            # exporter_config=ExporterConfig(exporter_type="STDOUT"),
            sampling_config=SamplingConfig(trace_sampling_type="ALWAYS"),
        )
    )

    # Setup the server
    stop_server = asyncio.Future()
    rpc_server = RPCServer(Messenger(URL, logger, name=RPC_SERVER_ID))
    await rpc_server.open()

    async def service_fun(payload: bytes, headers: dict) -> bytes:
        logger.debug(
            f"Service function is called with message: '{payload}' with headers: {headers}"
        )
        # stop_server.set_result(None)
        return b"service_fun response"

    logger.debug("RPC server start listening")
    await rpc_server.listen(TEST_TOPIC, service_fun=service_fun)

    logger.debug("Wait for service function callback")
    await asyncio.wait({stop_server})
    await rpc_server.close()
    oti.shutdown()


if __name__ == "__main__":
    asyncio.run(server())

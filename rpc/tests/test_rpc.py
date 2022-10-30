"""Test the rpc module"""
import unittest
from loguru import logger

import asyncio
from nats_messenger.messenger import Messenger
from rpc import RPCClient, RPCServer

"""Common configuration parameters for test cases"""

URL = "nats://127.0.0.1:4222"
CREDENTIALS = ""
CLUSTER_ID = "py-msgp-cluster"
RPC_CLIENT_ID = "test-client"
RPC_SERVER_ID = "test-server"
TEST_TOPIC = "test-rpc-topic-name"
TEST_PAYLOAD = b"test payload..."


class RPCTestCase(unittest.TestCase):
    """The RPC test cases functions"""

    def test_server_client(self) -> None:
        """Test the RPCServer.listen() and RPCClient.call() methods"""

        async def run():
            # Setup the server
            rpc_server = RPCServer(Messenger(URL, logger, name=RPC_SERVER_ID))
            await rpc_server.open()
            total_messages = 0
            callback_called = asyncio.Future()
            service_fun_response = b"service_fun response"

            async def service_fun(payload: bytes, headers: dict) -> bytes:
                nonlocal total_messages
                nonlocal callback_called
                logger.debug(f"Service function is called with message: '{payload}'")
                self.assertEqual(TEST_PAYLOAD, payload)
                total_messages += 1
                if total_messages >= 1:
                    callback_called.set_result(None)
                return service_fun_response, headers

            logger.debug("RPC server start listening")
            await rpc_server.listen(TEST_TOPIC, service_fun=service_fun)

            # Setup the client
            rpc_client = RPCClient(Messenger(URL, logger, name=RPC_CLIENT_ID))
            await rpc_client.open()

            # Call the server via the client
            logger.debug("Use client.call()")
            response, response_headers = await rpc_client.call(
                TEST_TOPIC, TEST_PAYLOAD, 1.0
            )
            self.assertEqual(service_fun_response, response)

            logger.debug("Wait for service function callback")
            await asyncio.wait_for(callback_called, 1)

            # Shut down the server and the client
            logger.debug("Close RPC server and client")
            await rpc_server.close()
            await rpc_client.close()

        asyncio.run(run())

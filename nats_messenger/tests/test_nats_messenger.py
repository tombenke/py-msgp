"""Test the messenger module"""
import unittest
from loguru import logger

import asyncio
from nats_messenger.messenger import Messenger


class MessengerTestCase(unittest.TestCase):
    """The Messenger test cases"""

    def test_open_close(self) -> None:
        """Test the Messenger open and close methods"""

        async def run():
            messenger = Messenger("", "", "py-messenger-cluster", "client-123", logger)
            await messenger.open()
            await messenger.close()

        asyncio.run(run())

        self.assertTrue(True)

    def test_publish_subscribe(self) -> None:
        """Test the Messenger's publish and subscribe methods"""

        async def run():
            messenger = Messenger("", "", "py-messenger-cluster", "client-123", logger)
            await messenger.open()
            total_messages = 0
            future = asyncio.Future()

            async def callback(msg: bytes):
                nonlocal total_messages
                nonlocal future
                logger.debug(f"Received a message: '{msg}'")
                total_messages += 1
                if total_messages >= 2:
                    future.set_result(None)

            subscriber = await messenger.subscribe("hi", callback=callback)

            logger.debug("Publish messages")
            await messenger.publish("hi", b"hello")
            await messenger.publish("hi", b"world")

            logger.debug("Wait for callbacks")
            await asyncio.wait_for(future, 1)

            logger.debug("Unsubscribe")
            await subscriber.unsubscribe()

            logger.debug("Close messenger")
            await messenger.close()

        asyncio.run(run())

        self.assertTrue(True)

    def test_request_response(self) -> None:
        """Test the Messenger's request and response methods"""

        async def run():
            messenger = Messenger("", "", "py-messenger-cluster", "client-123", logger)
            await messenger.open()
            total_messages = 0
            future = asyncio.Future()
            service_fun_response = b"service_fun response"

            async def service_fun(msg: bytes) -> bytes:
                nonlocal total_messages
                nonlocal future
                logger.debug(f"Service function is called with message: '{msg}'")
                total_messages += 1
                if total_messages >= 2:
                    future.set_result(None)
                return service_fun_response

            subscriber = await messenger.response("hi", service_fun=service_fun)

            logger.debug("Request messages")
            response = await messenger.request("hi", b"hello", 1.0)
            response = await messenger.request("hi", b"world", 1.0)
            self.assertEqual(service_fun_response, response)

            logger.debug("Wait for requests")
            await asyncio.wait_for(future, 1)

            logger.debug("Unsubscribe")
            await subscriber.unsubscribe()

            logger.debug("Close messenger")
            await messenger.close()

        asyncio.run(run())

        self.assertTrue(True)

"""Test the messenger module"""
import unittest
import asyncio
from loguru import logger

from nats_messenger.messenger import Messenger
from nats_messenger.tests.config_test import (
    URL,
    CREDENTIALS,
    CLUSTER_ID,
    CLIENT_ID,
    TEST_PAYLOAD,
    TEST_TOPIC,
)


class MessengerNonDurableTestCase(unittest.TestCase):
    """The Messenger test cases for non-durable functions"""

    def test_publish_subscribe(self) -> None:
        """Test the Messenger's publish and subscribe methods"""

        async def run():
            messenger = Messenger(URL, CREDENTIALS, CLUSTER_ID, CLIENT_ID, logger)
            await messenger.open()
            total_messages = 0
            callback_called = asyncio.Future()

            async def callback(msg: bytes):
                nonlocal total_messages
                nonlocal callback_called
                logger.debug(f"Received a message: '{msg}'")
                self.assertEqual(TEST_PAYLOAD, msg)
                total_messages += 1
                if total_messages >= 2:
                    callback_called.set_result(None)

            subscriber = await messenger.subscribe(TEST_TOPIC, callback=callback)

            logger.debug("Publish messages")
            await messenger.publish(TEST_TOPIC, TEST_PAYLOAD)
            await messenger.publish(TEST_TOPIC, TEST_PAYLOAD)

            logger.debug("Wait for callbacks")
            await asyncio.wait_for(callback_called, 1)

            logger.debug("Unsubscribe")
            await subscriber.unsubscribe()

            logger.debug("Close messenger")
            await messenger.close()

        asyncio.run(run())

    def test_request_response(self) -> None:
        """Test the Messenger's request and response methods"""

        async def run():
            messenger = Messenger(URL, CREDENTIALS, CLUSTER_ID, CLIENT_ID, logger)
            await messenger.open()
            total_messages = 0
            callback_called = asyncio.Future()
            service_fun_response = b"service_fun response"

            async def service_fun(payload: bytes) -> bytes:
                nonlocal total_messages
                nonlocal callback_called
                logger.debug(f"Service function is called with message: '{payload}'")
                self.assertEqual(TEST_PAYLOAD, payload)
                total_messages += 1
                if total_messages >= 2:
                    callback_called.set_result(None)
                return service_fun_response

            subscriber = await messenger.response(TEST_TOPIC, service_fun=service_fun)

            logger.debug("Request messages")
            response = await messenger.request(TEST_TOPIC, TEST_PAYLOAD, 1.0)
            response = await messenger.request(TEST_TOPIC, TEST_PAYLOAD, 1.0)
            self.assertEqual(service_fun_response, response)

            logger.debug("Wait for requests")
            await asyncio.wait_for(callback_called, 1)

            logger.debug("Unsubscribe")
            await subscriber.unsubscribe()

            logger.debug("Close messenger")
            await messenger.close()

        asyncio.run(run())

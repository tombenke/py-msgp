"""Test the messenger module"""
import unittest
import asyncio
from loguru import logger

from nats_messenger.messenger import Messenger
from nats_messenger.tests.config_test import (
    URL,
    CLIENT_ID,
    TEST_PAYLOAD,
    TEST_TOPIC,
    TEST_HEADERS,
)


class MessengerNonDurableTestCase(unittest.IsolatedAsyncioTestCase):
    """The Messenger test cases for non-durable functions"""

    def test_publish_subscribe(self) -> None:
        """Test the Messenger's publish and subscribe methods"""

        async def run():
            messenger = Messenger(URL, logger, name=CLIENT_ID)
            await messenger.open()
            total_messages = 0
            callback_called = asyncio.Future()

            async def callback(payload: bytes, headers: dict):
                nonlocal total_messages
                nonlocal callback_called
                logger.debug(
                    f"Received a message with payload: '{payload}', headers: {headers}"
                )
                self.assertEqual(TEST_PAYLOAD, payload)
                self.assertEqual(TEST_HEADERS, headers)
                total_messages += 1
                if total_messages >= 2:
                    callback_called.set_result(None)

            subscriber = await messenger.subscribe(TEST_TOPIC, callback=callback)

            logger.debug("Publish messages")
            await messenger.publish(TEST_TOPIC, TEST_PAYLOAD, headers=TEST_HEADERS)
            await messenger.publish(TEST_TOPIC, TEST_PAYLOAD, headers=TEST_HEADERS)

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
            messenger = Messenger(URL, logger)
            await messenger.open()
            total_messages = 0
            callback_called = asyncio.Future()
            service_fun_response = b"service_fun response"

            async def service_fun(payload: bytes, headers: dict) -> tuple[bytes, dict]:
                nonlocal total_messages
                nonlocal callback_called
                logger.debug(
                    f"Service function is called with message: payload: '{payload}, headers: {headers}'"
                )
                self.assertEqual(TEST_PAYLOAD, payload)
                self.assertEqual(TEST_HEADERS, headers)
                total_messages += 1
                if total_messages >= 2:
                    callback_called.set_result(None)
                return service_fun_response, TEST_HEADERS

            subscriber = await messenger.response(TEST_TOPIC, service_fun=service_fun)

            logger.debug("Request messages")
            response, response_headers = await messenger.request(
                TEST_TOPIC, TEST_PAYLOAD, 1.0, headers=TEST_HEADERS
            )
            response, response_headers = await messenger.request(
                TEST_TOPIC, TEST_PAYLOAD, 1.0, headers=TEST_HEADERS
            )
            self.assertEqual(service_fun_response, response)
            self.assertEqual(TEST_HEADERS, response_headers)

            logger.debug("Wait for requests")
            await asyncio.wait_for(callback_called, 1)

            logger.debug("Unsubscribe")
            await subscriber.unsubscribe()

            logger.debug("Close messenger")
            await messenger.close()

        asyncio.run(run())

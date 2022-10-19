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


class MessengerDurableTestCase(unittest.TestCase):
    """The Messenger test cases for durable functions"""

    def test_publish_subscribe_durable(self) -> None:
        """Test the Messenger's synchronous publish and subscribe methods with durable subject"""

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

            subscriber = await messenger.subscribe_durable(
                TEST_TOPIC, callback=callback
            )

            logger.debug("Publish messages")
            await messenger.publish_durable(TEST_TOPIC, TEST_PAYLOAD)
            await messenger.publish_durable(TEST_TOPIC, TEST_PAYLOAD)

            logger.debug("Wait for callbacks")
            await asyncio.wait_for(callback_called, 1)

            logger.debug("Unsubscribe")
            await subscriber.unsubscribe()

            logger.debug("Close messenger")
            await messenger.close()

        asyncio.run(run())

    def test_publish_async_subscribe_durable(self) -> None:
        """Test the Messenger's asynchronous publish and subscribe methods with durable subject"""

        async def run():
            messenger = Messenger(URL, CREDENTIALS, CLUSTER_ID, CLIENT_ID, logger)
            await messenger.open()
            total_messages = 0
            callback_called = asyncio.Future()
            total_ack_messages = 0
            ack_called = asyncio.Future()

            async def callback(msg: bytes):
                nonlocal total_messages
                nonlocal callback_called
                logger.debug(f"Received a message: '{msg}'")
                self.assertEqual(TEST_PAYLOAD, msg)
                total_messages += 1
                if total_messages >= 2:
                    callback_called.set_result(None)

            subscriber = await messenger.subscribe_durable(
                TEST_TOPIC, callback=callback
            )

            async def ack_handler(ack):
                nonlocal total_ack_messages
                nonlocal ack_called
                logger.debug(f"the ack_handler of publish_async is called with '{ack}'")
                total_ack_messages += 1
                if total_ack_messages >= 2:
                    ack_called.set_result(None)

            logger.debug("Publish messages")
            await messenger.publish_async_durable(
                TEST_TOPIC, TEST_PAYLOAD, ack_handler=ack_handler
            )
            await messenger.publish_async_durable(
                TEST_TOPIC, TEST_PAYLOAD, ack_handler=ack_handler
            )

            logger.debug("Wait for publish acknowledgements")
            await asyncio.wait_for(ack_called, 1)

            logger.debug("Wait for callbacks")
            await asyncio.wait_for(callback_called, 1)

            logger.debug("Unsubscribe")
            await subscriber.unsubscribe()

            logger.debug("Close messenger")
            await messenger.close()

        asyncio.run(run())

    def test_publish_subscribe_durable_with_ack(self) -> None:
        """Test the Messenger's synchronous publish and subscribe methods with durable subject using manual acknowledge"""

        async def run():
            messenger = Messenger(URL, CREDENTIALS, CLUSTER_ID, CLIENT_ID, logger)
            await messenger.open()
            total_messages = 0
            callback_called = asyncio.Future()

            async def callback(msg: bytes) -> bool:
                nonlocal total_messages
                nonlocal callback_called
                total_messages += 1
                if total_messages >= 2:
                    callback_called.set_result(None)
                logger.debug(
                    f"Received a message: '{msg}' total_messages: {total_messages}"
                )
                self.assertEqual(TEST_PAYLOAD, msg)
                return True

            subscriber = await messenger.subscribe_durable_with_ack(
                TEST_TOPIC, callback=callback
            )

            logger.debug("Publish messages")
            await messenger.publish_durable(TEST_TOPIC, TEST_PAYLOAD)
            await messenger.publish_durable(TEST_TOPIC, TEST_PAYLOAD)

            logger.debug("Wait for callbacks")
            await asyncio.wait_for(callback_called, 1)

            await subscriber.unsubscribe()
            logger.debug("Close messenger")
            await messenger.close()

        asyncio.run(run())

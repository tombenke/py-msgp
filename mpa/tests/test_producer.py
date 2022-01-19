"""Test the mpa module"""
import unittest
import asyncio
from loguru import logger
from nats_messenger import Messenger
from mpa import MessageProducerActor
from mpa.tests.config_test import (
    URL,
    CREDENTIALS,
    CLUSTER_ID,
    CONSUMER_CLIENT_ID,
    PRODUCER_MPA_CLIENT_ID,
    OUTBOUND_TOPIC,
    TEST_PAYLOAD,
)


class ProducerMPATestCase(unittest.TestCase):
    """The Producer MPA test cases functions"""

    def test_producer_actor(self) -> None:
        """Test the MessageProducerActor"""

        async def run():
            logger.debug("Setup the test consumer")
            total_consumer_messages = 0
            consumer_callback_called = asyncio.Future()

            async def consumer_callback(msg: bytes):
                nonlocal total_consumer_messages
                nonlocal consumer_callback_called
                logger.debug(f"Received a message: '{msg}'")
                self.assertEqual(actor_function_response, msg)
                total_consumer_messages += 1
                if total_consumer_messages >= 2:
                    consumer_callback_called.set_result(None)

            consumer = Messenger(
                URL, CREDENTIALS, CLUSTER_ID, CONSUMER_CLIENT_ID, logger
            )
            await consumer.open()
            await consumer.subscribe(OUTBOUND_TOPIC, callback=consumer_callback)

            logger.debug("Setup the producer actor")
            total_messages = 0
            actor_function_called = asyncio.Future()
            actor_function_response = b"actor function response..."

            async def actor_function(payload: bytes) -> bytes:
                nonlocal total_messages
                nonlocal actor_function_called
                logger.debug(
                    f"Producer actor_function is called with message: '{payload}'"
                )
                self.assertEqual(TEST_PAYLOAD, payload)
                total_messages += 1
                if total_messages >= 2:
                    actor_function_called.set_result(None)
                return actor_function_response

            producer_actor = MessageProducerActor(
                Messenger(URL, CREDENTIALS, CLUSTER_ID, PRODUCER_MPA_CLIENT_ID, logger),
                OUTBOUND_TOPIC,
                actor_function,
                durable=False,
            )
            await producer_actor.open()

            logger.debug("Produce something")
            await producer_actor.next(TEST_PAYLOAD)
            await producer_actor.next(TEST_PAYLOAD)

            logger.debug("Wait for actor function callback and consumer callback")
            await asyncio.wait_for(actor_function_called, 1)
            await asyncio.wait_for(consumer_callback_called, 1)

            # Shut down the producer actor and the producer
            await producer_actor.close()
            await consumer.close()

        asyncio.run(run())

    def test_producer_actor_durable(self) -> None:
        """Test the MessageProducerActor using durable message channel"""

        async def run():
            logger.debug("Setup the test consumer")
            total_consumer_messages = 0
            consumer_callback_called = asyncio.Future()

            async def consumer_callback(msg: bytes):
                nonlocal total_consumer_messages
                nonlocal consumer_callback_called
                logger.debug(f"Received a message: '{msg}'")
                self.assertEqual(actor_function_response, msg)
                total_consumer_messages += 1
                if total_consumer_messages >= 2:
                    consumer_callback_called.set_result(None)

            consumer = Messenger(
                URL, CREDENTIALS, CLUSTER_ID, CONSUMER_CLIENT_ID, logger
            )
            await consumer.open()
            await consumer.subscribe_durable(OUTBOUND_TOPIC, callback=consumer_callback)

            logger.debug("Setup the producer actor")
            total_messages = 0
            actor_function_called = asyncio.Future()
            actor_function_response = b"actor function response..."

            async def actor_function(payload: bytes) -> bytes:
                nonlocal total_messages
                nonlocal actor_function_called
                logger.debug(
                    f"Producer actor_function is called with message: '{payload}'"
                )
                self.assertEqual(TEST_PAYLOAD, payload)
                total_messages += 1
                if total_messages >= 2:
                    actor_function_called.set_result(None)
                return actor_function_response

            producer_actor = MessageProducerActor(
                Messenger(URL, CREDENTIALS, CLUSTER_ID, PRODUCER_MPA_CLIENT_ID, logger),
                OUTBOUND_TOPIC,
                actor_function,
                durable=True,
            )
            await producer_actor.open()

            logger.debug("Produce something")
            await producer_actor.next(TEST_PAYLOAD)
            await producer_actor.next(TEST_PAYLOAD)

            logger.debug("Wait for actor function callback and consumer callback")
            await asyncio.wait_for(actor_function_called, 1)
            await asyncio.wait_for(consumer_callback_called, 1)

            # Shut down the producer actor and the producer
            await producer_actor.close()
            await consumer.close()

        asyncio.run(run())

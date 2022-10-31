"""Test the mpa module"""
import unittest
import asyncio
from loguru import logger
from nats_messenger import Messenger
from mpa import MessageConsumerActor
from mpa.tests.config_test import (
    URL,
    PRODUCER_CLIENT_ID,
    CONSUMER_MPA_CLIENT_ID,
    DURABLE_INBOUND_TOPIC,
    INBOUND_TOPIC,
    TEST_PAYLOAD,
)


class ConsumerMPATestCase(unittest.TestCase):
    """The Consumer MPA test cases functions"""

    def test_consumer_actor(self) -> None:
        """Test the MessageConsumerActor"""

        async def run():
            # Setup the consumer actor
            total_messages = 0
            actor_function_called = asyncio.Future()
            actor_function_response = b"actor function response..."

            async def actor_function(
                payload: bytes, headers: dict
            ) -> tuple[bytes, dict]:
                nonlocal total_messages
                nonlocal actor_function_called
                logger.debug(
                    f"Consumer actor_function is called with message: '{payload}' with headers: {headers}"
                )
                self.assertEqual(TEST_PAYLOAD, payload)
                total_messages += 1
                if total_messages >= 2:
                    actor_function_called.set_result(None)
                return actor_function_response, headers

            consumer_actor = MessageConsumerActor(
                Messenger(URL, logger, name=CONSUMER_MPA_CLIENT_ID),
                INBOUND_TOPIC,
                actor_function,
                durable=False,
            )
            await consumer_actor.open()

            logger.debug("Send something to consume")
            producer = Messenger(URL, logger, name=PRODUCER_CLIENT_ID)
            await producer.open()
            await producer.publish(INBOUND_TOPIC, TEST_PAYLOAD)
            await producer.publish(INBOUND_TOPIC, TEST_PAYLOAD)

            logger.debug("Wait for actor function callback")
            await asyncio.wait_for(actor_function_called, 1)

            # Shut down the consumer actor and the producer
            await consumer_actor.close()
            await producer.close()

        asyncio.run(run())

    def test_consumer_actor_durable(self) -> None:
        """Test the MessageConsumerActor using durable message channel"""

        async def run():
            # Setup the consumer actor
            total_messages = 0
            actor_function_called = asyncio.Future()
            actor_function_response = b"actor function response..."

            async def actor_function(
                payload: bytes, headers: dict
            ) -> tuple[bytes, dict]:
                nonlocal total_messages
                nonlocal actor_function_called
                logger.debug(
                    f"Consumer actor_function is called with message: '{payload}' with headers: {headers}"
                )
                self.assertEqual(TEST_PAYLOAD, payload)
                total_messages += 1
                if total_messages >= 2:
                    actor_function_called.set_result(None)
                return actor_function_response, headers

            consumer_actor = MessageConsumerActor(
                Messenger(URL, logger, name=CONSUMER_MPA_CLIENT_ID),
                DURABLE_INBOUND_TOPIC,
                actor_function,
                durable=True,
            )
            await consumer_actor.open()

            logger.debug("Send something to consume")
            producer = Messenger(URL, logger, name=PRODUCER_CLIENT_ID)
            await producer.open()
            await producer.publish_durable(DURABLE_INBOUND_TOPIC, TEST_PAYLOAD)
            await producer.publish_durable(DURABLE_INBOUND_TOPIC, TEST_PAYLOAD)

            logger.debug("Wait for actor function callback")
            await asyncio.wait_for(actor_function_called, 1)

            # Shut down the consumer actor and the producer
            await consumer_actor.close()
            await producer.close()

        asyncio.run(run())

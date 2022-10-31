"""Test the mpa module"""
import unittest
import asyncio
from loguru import logger
from nats_messenger import Messenger
from mpa import MessageProcessorActor
from mpa.tests.config_test import (
    URL,
    PRODUCER_CLIENT_ID,
    CONSUMER_CLIENT_ID,
    PROCESSOR_MPA_CLIENT_ID,
    INBOUND_TOPIC,
    DURABLE_INBOUND_PROC_TOPIC,
    OUTBOUND_TOPIC,
    DURABLE_OUTBOUND_PROC_TOPIC,
    TEST_PAYLOAD,
)


class ProcessorMPATestCase(unittest.TestCase):
    """The Processor MPA test cases functions"""

    def test_processor_actor(self) -> None:
        """Test the MessageProcessorActor"""

        async def run():
            logger.debug("Setup the test consumer")
            total_consumer_messages = 0
            consumer_callback_called = asyncio.Future()

            async def consumer_callback(msg: bytes, headers: dict):
                nonlocal total_consumer_messages
                nonlocal consumer_callback_called
                logger.debug(f"Received a message: '{msg}' with headers: {headers}")
                self.assertEqual(actor_function_response, msg)
                total_consumer_messages += 1
                if total_consumer_messages >= 2:
                    consumer_callback_called.set_result(None)

            consumer = Messenger(URL, logger, name=CONSUMER_CLIENT_ID)
            await consumer.open()
            await consumer.subscribe(OUTBOUND_TOPIC, callback=consumer_callback)

            logger.debug("Setup the processor actor")
            total_messages = 0
            actor_function_called = asyncio.Future()
            actor_function_response = b"actor function response..."

            async def actor_function(
                payload: bytes, headers: dict
            ) -> tuple[bytes, dict]:
                nonlocal total_messages
                nonlocal actor_function_called
                logger.debug(
                    f"Processor actor_function is called with message: '{payload}' with headers: {headers}"
                )
                self.assertEqual(TEST_PAYLOAD, payload)
                total_messages += 1
                if total_messages >= 2:
                    actor_function_called.set_result(None)
                return actor_function_response, headers

            processor_actor = MessageProcessorActor(
                Messenger(URL, logger, name=PROCESSOR_MPA_CLIENT_ID),
                INBOUND_TOPIC,
                OUTBOUND_TOPIC,
                actor_function,
                durable_in=False,
                durable_out=False,
            )
            await processor_actor.open()

            logger.debug("Send something to consume")
            producer = Messenger(URL, logger, name=PRODUCER_CLIENT_ID)
            await producer.open()
            await producer.publish(INBOUND_TOPIC, TEST_PAYLOAD)
            await producer.publish(INBOUND_TOPIC, TEST_PAYLOAD)

            logger.debug("Wait for actor function callback and consumer callback")
            await asyncio.wait_for(actor_function_called, 1)
            await asyncio.wait_for(consumer_callback_called, 1)

            # Shut down the processor actor, the consumer and the producer
            await processor_actor.close()
            await consumer.close()
            await producer.close()

        asyncio.run(run())

    def test_processor_actor_durable(self) -> None:
        """Test the MessageProcessorActor"""

        async def run():
            logger.debug("Setup the test consumer")
            total_consumer_messages = 0
            consumer_callback_called = asyncio.Future()

            async def consumer_callback(msg: bytes, headers: dict):
                nonlocal total_consumer_messages
                nonlocal consumer_callback_called
                logger.debug(f"Received a message: '{msg}' with headers: {headers}")
                self.assertEqual(actor_function_response, msg)
                total_consumer_messages += 1
                if total_consumer_messages >= 2:
                    consumer_callback_called.set_result(None)

            consumer = Messenger(URL, logger, name=CONSUMER_CLIENT_ID)
            await consumer.open()
            await consumer.subscribe_durable(
                DURABLE_OUTBOUND_PROC_TOPIC, callback=consumer_callback
            )

            logger.debug("Setup the processor actor")
            total_messages = 0
            actor_function_called = asyncio.Future()
            actor_function_response = b"actor function response..."

            async def actor_function(
                payload: bytes, headers: dict
            ) -> tuple[bytes, dict]:
                nonlocal total_messages
                nonlocal actor_function_called
                logger.debug(
                    f"Processor actor_function is called with message: '{payload}' with headers: {headers}"
                )
                self.assertEqual(TEST_PAYLOAD, payload)
                total_messages += 1
                if total_messages >= 2:
                    actor_function_called.set_result(None)
                return actor_function_response, headers

            processor_actor = MessageProcessorActor(
                Messenger(URL, logger, name=PROCESSOR_MPA_CLIENT_ID),
                DURABLE_INBOUND_PROC_TOPIC,
                DURABLE_OUTBOUND_PROC_TOPIC,
                actor_function,
                durable_in=True,
                durable_out=True,
            )
            await processor_actor.open()

            logger.debug("Send something to consume")
            producer = Messenger(URL, logger, name=PRODUCER_CLIENT_ID)
            await producer.open()
            await producer.publish_durable(DURABLE_INBOUND_PROC_TOPIC, TEST_PAYLOAD)
            await producer.publish_durable(DURABLE_INBOUND_PROC_TOPIC, TEST_PAYLOAD)

            logger.debug("Wait for actor function callback and consumer callback")
            await asyncio.wait_for(actor_function_called, 1)
            await asyncio.wait_for(consumer_callback_called, 1)

            # Shut down the processor actor, the consumer and the producer
            await processor_actor.close()
            await consumer.close()
            await producer.close()

        asyncio.run(run())

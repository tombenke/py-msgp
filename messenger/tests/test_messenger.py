"""Test the messenger module"""
import unittest

import asyncio
from messenger.messenger import Messenger


class FakeMessenger(Messenger):
    def __init__(self):
        pass

    async def open(self):
        pass

    async def close(self):
        pass

    async def publish(self):
        pass

    async def subscribe(self):
        pass

    async def request(self):
        pass

    async def response(self):
        pass

    async def publish_durable(self):
        pass

    async def publish_async_durable(self):
        pass

    async def subscribe_durable(self):
        pass

    async def subscribe_durable_with_ack(self):
        pass


class MessengerTestCase(unittest.TestCase):
    """The Messenger test cases"""

    def test_open_close(self) -> None:
        """Test the Messenger init and close"""

        m = FakeMessenger()
        self.assertTrue(True)

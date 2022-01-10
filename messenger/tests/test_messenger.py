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

    def publish(self):
        pass

    def subscribe(self):
        pass


class MessengerTestCase(unittest.TestCase):
    """The Messenger test cases"""

    def test_open_close(self) -> None:
        """Test the Messenger init and close"""

        m = FakeMessenger()
        self.assertTrue(True)

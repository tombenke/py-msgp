"""Test the messenger module"""
import unittest
from loguru import logger

import asyncio
from nats_messenger.messenger import Messenger
from nats_messenger.tests.config_test import *


class MessengerInitTestCase(unittest.TestCase):
    """The Messenger test cases for open and close functions"""

    def test_open_close(self) -> None:
        """Test the Messenger open and close methods"""

        async def run():
            messenger = Messenger(URL, CREDENTIALS, CLUSTER_ID, CLIENT_ID, logger)
            await messenger.open()
            await messenger.close()

        asyncio.run(run())

        self.assertTrue(True)

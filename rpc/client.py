"""
The RPCClient class, which represents the unit that can be used an RPC client via messaging.
"""
import asyncio
from typing import Callable
from messenger.messenger import Messenger
from messenger.subscriber import Subscriber


class RPCClient:
    """
    RPCClient represents the unit that can be used as an RPC client via messaging.
    It is the request part of a simple wrapper over the request/response pattern provided by the underlining Messenger class.
    """

    def __init__(self, messenger: Messenger):
        """
        Constructor for the RPCClient
        """
        self.messenger: Messenger = messenger

    async def open(self):
        """
        Opens the connection to the messaging via the messenger
        """
        await self.messenger.open()

    async def close(self):
        """
        Close the connection to the messaging via the messenger
        """
        await self.messenger.close()

    async def call(self, subject: str, request: bytes, timeout: float) -> bytes:
        """
        Provides the client endpoint with a raw request
        to call the server function at the server side of the RPC connection.
        """
        return await self.messenger.request(subject, request, timeout)

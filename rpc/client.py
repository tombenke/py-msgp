"""
The RPCClient class, which represents the unit that can be used an RPC client via messaging.
"""
from loguru import logger
from messenger.messenger import Messenger


class RPCClient:
    """
    RPCClient represents the unit that can be used as an RPC client via messaging.
    It is the request part of a simple wrapper over the request/response pattern provided by the underlining Messenger class.
    """

    def __init__(self, messenger: Messenger, _logger=logger):
        """
        Constructor for the RPCClient
        """
        self.messenger: Messenger = messenger
        self.logger = _logger

    async def open(self):
        """
        Opens the connection to the messaging via the messenger
        """
        self.logger.debug("RPCClient.open()")
        await self.messenger.open()

    async def close(self):
        """
        Close the connection to the messaging via the messenger
        """
        self.logger.debug("RPCClient.close()")
        await self.messenger.close()

    async def call(self, subject: str, request: bytes, timeout: float) -> bytes:
        """
        Provides the client endpoint with a raw request
        to call the server function at the server side of the RPC connection.
        """
        self.logger.debug(f"RPCClient.call('{subject}', '{request}')")
        return await self.messenger.request(subject, request, timeout)

"""
The RPCServer class, which represents the unit that can be used an RPC server via messaging.
"""
from typing import Callable
from loguru import logger
from messenger.messenger import Messenger
from messenger.subscriber import Subscriber


class RPCServer:
    """
    RPCServer represents the unit that can be used as an RPC server via messaging.
    It is the resonse part of a simple wrapper over the request/response pattern
    provided by the underlining Messenger class.
    """

    def __init__(self, messenger: Messenger, _logger=logger):
        """
        Constructor for the RPCServer
        """
        self.messenger: Messenger = messenger
        self.subscriber: Subscriber = None
        self.logger = _logger

    async def open(self):
        """
        Opens the connection to the messaging via the messenger
        """
        self.logger.debug("RPCServer.open()")
        await self.messenger.open()

    async def close(self):
        """
        Close the connection to the messaging via the messenger
        """
        self.logger.debug("RPCServer.close()")
        if self.subscriber is not None:
            await self.subscriber.unsubscribe()

        await self.messenger.close()

    async def listen(self, subject: str, service_fun: Callable[[bytes], bytes]):
        """
        Registers a server function to a messaging subject.
        The server's function will be called when an RPCClient sends a request to this subject.
        The server replies a response message that the client will get.
        """
        self.logger.debug(f"RPCServer.listen('{subject}')")
        self.subscriber = await self.messenger.response(subject, service_fun)

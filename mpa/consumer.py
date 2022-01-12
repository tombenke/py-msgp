"""
The MessageConsumerActor class.
"""
from typing import Callable
from loguru import logger
from messenger.messenger import Messenger
from messenger.subscriber import Subscriber


class MessageConsumerActor:
    """
    MessageConsumerActor is an actor, that subscribes to a topic, and consumes the incoming messages.
    The incoming messages are handed over to an actor function, that implements the business logic.
    """

    def __init__(
        self,
        messenger: Messenger,
        inbound_subject: str,
        actor_function: Callable[[bytes], bytes],
        durable=True,
        _logger=logger,
    ):
        """
        Constructor for the MessageConsumerActor
        """
        self.messenger: Messenger = messenger
        self.inbound_subject = inbound_subject
        self.durable = durable
        self.subscriber: Subscriber = None
        self.actor_function = actor_function
        self.logger = _logger

    async def open(self):
        """
        Opens the connection to the messaging via the messenger
        It also registers an actor function, that will process the incoming messages.
        """
        self.logger.debug("MessageConsumerActor.open()")
        await self.messenger.open()
        if self.durable:
            self.subscriber = await self.messenger.subscribe_durable_with_ack(
                self.inbound_subject, self.actor_function
            )
        else:
            self.subscriber = await self.messenger.subscribe(
                self.inbound_subject, self.actor_function
            )

    async def close(self):
        """
        Close the connection to the messaging via the messenger
        """
        self.logger.debug("MessageConsumerActor.close()")
        if self.subscriber is not None:
            await self.subscriber.unsubscribe()

        await self.messenger.close()

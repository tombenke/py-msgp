"""
The MessageProcessorActor class.
"""
from typing import Callable
from loguru import logger
from messenger.messenger import Messenger
from messenger.subscriber import Subscriber


class MessageProcessorActor:
    """
    MessageProcessorActor is an actor, that both consumes and produces messages,
    and processes in-between receiving and sending the inbound messages.
    It subscribes to an inbound topic and consumes the incoming messages.
    The incoming messages are handed over to an actor function, that implements the business logic.
    Finally the processed messages will be sent to the outbound topic.
    """

    def __init__(
        self,
        messenger: Messenger,
        inbound_subject: str,
        outbound_subject: str,
        actor_function: Callable[[bytes], bytes],
        durable_in=True,
        durable_out=True,
        _logger=logger,
    ):
        """
        Constructor for the MessageProcessorActor
        """
        self.messenger: Messenger = messenger
        self.inbound_subject = inbound_subject
        self.outbound_subject = outbound_subject
        self.durable_in = durable_in
        self.durable_out = durable_out
        self.subscriber: Subscriber = None
        self.actor_function = actor_function
        self.logger = _logger

    async def open(self):
        """
        Opens the connection to the messaging via the messenger
        It also registers an actor function, that will process the incoming messages.
        """
        self.logger.debug("MessageProcessorActor.open()")
        await self.messenger.open()

        async def actor_function_wrapper(payload: bytes) -> None:
            outbound_payload = await self.actor_function(payload)
            self.logger.debug(
                f"MessageProcessorActor.actor_wrapper({payload}) -> '{outbound_payload}'"
            )
            if self.durable_out:
                await self.messenger.publish_durable(
                    self.outbound_subject, outbound_payload
                )
            else:
                await self.messenger.publish(self.outbound_subject, outbound_payload)

        if self.durable_in:
            self.subscriber = await self.messenger.subscribe_durable_with_ack(
                self.inbound_subject, actor_function_wrapper
            )
        else:
            self.subscriber = await self.messenger.subscribe(
                self.inbound_subject, actor_function_wrapper
            )

    async def close(self):
        """
        Close the connection to the messaging via the messenger
        """
        self.logger.debug("MessageProcessorActor.close()")
        if self.subscriber is not None:
            await self.subscriber.unsubscribe()

        await self.messenger.close()

"""
The MessageProducerActor class.
"""
from typing import Callable
from loguru import logger
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from messenger.messenger import Messenger


class MessageProducerActor:
    """
    MessageProducerActor is an actor, that publishes messages to a topic.
    The outgoing messages are optionally passed through an actor function,
    that may implement some extensional business logic.
    """

    def __init__(
        self,
        messenger: Messenger,
        outbound_subject: str,
        actor_function: Callable[[bytes], bytes] = None,
        durable=True,
        _logger=logger,
    ):
        """
        Constructor for the MessageProducerActor
        """
        self.messenger: Messenger = messenger
        self.outbound_subject = outbound_subject
        self.durable = durable
        self.actor_function = actor_function
        self.logger = _logger

    async def open(self):
        """
        Opens the connection to the messaging via the messenger
        It also registers an actor function, that will process the incoming messages.
        """
        self.logger.debug("MessageProducerActor.open()")
        await self.messenger.open()

    async def close(self):
        """
        Close the connection to the messaging via the messenger
        """
        self.logger.debug("MessageProducerActor.close()")
        await self.messenger.close()

    async def next(self, payload: bytes, headers=None):
        """
        The next method hands over the `payload` to the actor function of this producer-only MPA,
        that forwards it to the outbound channel.
        """
        outbound_payload = payload
        outbound_headers = headers
        tracer = trace.get_tracer(__name__)
        propagator = TraceContextTextMapPropagator()
        if headers is None:
            headers = {}
        ctx = propagator.extract(headers)

        with tracer.start_as_current_span(
            f"{self.outbound_subject} send", kind=trace.SpanKind.PRODUCER, context=ctx
        ) as span:
            if span.is_recording():
                span.set_attribute("messaging.system", "NATS")
                span.add_event(
                    "log",
                    {
                        "log.severity": "INFO",
                        "log.message": f"MPA producer publish through {self.outbound_subject} subject",
                    },
                )
                propagator.inject(headers)
                self.logger.debug(f"next() headers with context: {headers}")

            if self.actor_function is not None:
                outbound_payload, outbound_headers = await self.actor_function(
                    payload, headers=headers
                )
            else:
                outbound_headers = headers

            if self.durable:
                await self.messenger.publish_durable(
                    self.outbound_subject, outbound_payload, headers=outbound_headers
                )
            else:
                await self.messenger.publish(
                    self.outbound_subject, outbound_payload, headers=outbound_headers
                )

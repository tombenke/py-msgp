"""
The MessageConsumerActor class.
"""
from typing import Callable
from loguru import logger
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from messenger.messenger import Messenger, Subscriber


class MessageConsumerActor:
    """
    MessageConsumerActor is an actor, that subscribes to a topic, and consumes the incoming messages.
    The incoming messages are handed over to an actor function, that implements the business logic.
    """

    def __init__(
        self,
        messenger: Messenger,
        inbound_subject: str,
        actor_function: Callable[[bytes, dict], tuple[bytes, dict]],
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

        def actor_fun_wrapper(actor_fun):
            async def actor_fun_wrapped(
                payload: bytes, headers: dict
            ) -> tuple[bytes, dict]:
                tracer = trace.get_tracer(__name__)
                self.logger.debug(
                    f"actor_fun_wrapped() headers with context: {headers}"
                )
                propagator = TraceContextTextMapPropagator()
                if headers is None:
                    headers = {}
                ctx = propagator.extract(headers)
                with tracer.start_as_current_span(
                    f"{self.inbound_subject} receive",
                    kind=trace.SpanKind.CONSUMER,
                    context=ctx,
                ) as span:
                    self.logger.debug(f"span: {span} ctx: {ctx}")
                    if span.is_recording():
                        span.set_attribute("messaging.system", "NATS")
                        span.add_event(
                            "log",
                            {
                                "log.severity": "INFO",
                                "log.message": f"MPA consumer service function call through the {self.inbound_subject} subject",
                            },
                        )
                    response, response_headers = await actor_fun(payload, headers)
                return response, response_headers

            return actor_fun_wrapped

        if self.durable:
            self.subscriber = await self.messenger.subscribe_durable_with_ack(
                self.inbound_subject, actor_fun_wrapper(self.actor_function)
            )
        else:
            self.subscriber = await self.messenger.subscribe(
                self.inbound_subject, actor_fun_wrapper(self.actor_function)
            )

    async def close(self):
        """
        Close the connection to the messaging via the messenger
        """
        self.logger.debug("MessageConsumerActor.close()")
        if self.subscriber is not None:
            await self.subscriber.unsubscribe()

        await self.messenger.close()

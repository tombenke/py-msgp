"""
The MessageProcessorActor class.
"""
from typing import Callable
from loguru import logger
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from messenger.messenger import Messenger, Subscriber


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
        actor_function: Callable[[bytes, dict], bytes],
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

        async def actor_function_wrapper(
            payload: bytes, headers: dict
        ) -> tuple[bytes, dict]:
            outbound_payload = payload
            outbound_headers = headers
            tracer = trace.get_tracer(__name__)
            propagator = TraceContextTextMapPropagator()
            if headers is None:
                headers = {}
            ctx = propagator.extract(headers)
            with tracer.start_as_current_span(
                f"{self.inbound_subject} process",
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
                            "log.message": f"MPA processor actor function call from {self.inbound_subject} to {self.outbound_subject} subject",
                        },
                    )
                outbound_payload, outbound_headers = await self.actor_function(
                    payload, headers
                )
            self.logger.debug(
                f"MessageProcessorActor.actor_function_wrapper(payload: {payload}, headers: {headers}) ->"
                f"'payload: {outbound_payload}, headers: {outbound_headers}'"
            )

            propagator.inject(outbound_headers)
            if self.durable_out:
                await self.messenger.publish_durable(
                    self.outbound_subject, outbound_payload, outbound_headers
                )
            else:
                await self.messenger.publish(
                    self.outbound_subject, outbound_payload, outbound_headers
                )
            return outbound_payload, outbound_headers

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

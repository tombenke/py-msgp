"""
The RPCClient class, which represents the unit that can be used an RPC client via messaging.
"""
from typing import Optional
from loguru import logger
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
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

    async def call(
        self,
        subject: str,
        payload: bytes,
        timeout: float,
        headers: Optional[dict] = None,
    ) -> tuple[bytes, dict]:
        """
        Provides the client endpoint with a raw request
        to call the server function at the server side of the RPC connection.
        """

        if headers is None:
            headers = {}
        self.logger.debug(
            f"RPCClient.call('subject:{subject}', payload:'{payload}', headers:{headers})"
        )
        tracer = trace.get_tracer(__name__)
        propagator = TraceContextTextMapPropagator()
        ctx = propagator.extract(headers)
        with tracer.start_as_current_span(
            f"RPC/{subject}", kind=trace.SpanKind.CLIENT, context=ctx
        ) as span:
            if span.is_recording():
                span.set_attribute("rpc.service", "RPC")
                span.set_attribute("rpc.method", f"{subject}")
                span.add_event(
                    "log",
                    {
                        "log.severity": "INFO",
                        "log.message": f"RPC client call through the {subject} subject",
                    },
                )
                # Write the current context into the carrier.
                propagator.inject(headers)
                self.logger.debug(f"carrier: {headers}")
            response, response_headers = await self.messenger.request(
                subject, payload, timeout, headers=headers
            )
        return response, response_headers

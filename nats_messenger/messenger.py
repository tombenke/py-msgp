"""The NATS/NATS-Streaming implementation of the Messeger class"""
import asyncio
from typing import Callable
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN
from messenger import messenger
from messenger import subscriber
from nats_messenger.subscriber import Subscriber


class Messenger(messenger.Messenger):
    """
    The Messenger class that provides the implementation of the generic messaging pattern methods
    defined by the `messenger.Messenger` absctract class.
    This implementation uses the NATS and NATS streaming messaging middleware.
    """

    def __init__(
        self, url: str, credentials: str, cluster_id: str, client_id: str, logger
    ):
        """
        Constructor for a Messenger
        """

        self.url = url
        self.credentials = credentials
        self.cluster_id = cluster_id
        self.client_id = client_id
        self.logger = logger
        self.nats_conn: NATS
        self.stan_conn: STAN

    async def open(self):
        """
        Opens the connection to the messaging middleware
        """

        # Use borrowed connection for NATS then mount NATS Streaming
        # client on top.
        self.logger.debug("Connect to NATS")
        self.nats_conn = NATS()
        await self.nats_conn.connect(io_loop=asyncio.get_event_loop())

        # Start session with NATS Streaming cluster.
        self.logger.debug("Connect to STAN")
        self.stan_conn = STAN()
        await self.stan_conn.connect(
            self.cluster_id, self.client_id, nats=self.nats_conn
        )

    async def close(self):
        """
        Closes the connection to the messaging middleware
        """

        # Close NATS Streaming session
        self.logger.debug("Close to STAN")
        await self.stan_conn.close()

        # We are using a NATS borrowed connection so we need to close manually.
        self.logger.debug("Close to NATS")
        await self.nats_conn.close()

    async def publish(self, subject: str, payload: bytes):
        """
        Publishes `payload` message to the `subject` topic
          :param subject: Subject to which the message will be published.
          :param payload: Message data.
        """
        self.logger.debug(f"Publish to {subject} the payload '{payload}'")
        await self.nats_conn.publish(subject=subject, payload=payload)

    async def subscribe(
        self, subject: str, callback: Callable[[bytes], None]
    ) -> subscriber.Subscriber:
        """
        Subscribes to the `subject` topic, and calls the `callback` function with the inbound messages
        so the messages will be processed asychronously.
          :param subject: Subject that the subscriber will observe.
          :param callback: a Callable function, that the subscriber will call.
        """

        async def nats_callback(msg):
            self.logger.debug(f"Subscription callback function is called with '{msg}'")
            await callback(msg.data)

        subscription = await self.nats_conn.subscribe(subject=subject, cb=nats_callback)
        self.logger.debug(f"subscription type: {type(subscription)}")
        subs = Subscriber(self.nats_conn, subscription)
        self.logger.debug(f"Subscribed to {subject} via subscriber: {subs}")
        return subs

    async def request(self, subject: str, payload: bytes, timeout: float):
        """
        Send `payload` as a request message through the `subject` topic and expects a response until `timeout`.
        Returns with a future that is the response.
          :param subject: Subject to which the request will be sent.
          :param payload: Message data.
          :param timeout: Timeout in seconds, until the request waits for the response.
        """
        self.logger.debug(f"Send request {subject} with payload '{payload}'")
        response = await self.nats_conn.request(
            subject=subject, payload=payload, timeout=timeout
        )
        self.logger.debug(f"got response {response}")
        return response.data

    async def response(self, subject: str, service_fun: Callable[[bytes], None]):
        """
        Subscribes to the `subject` topic, and calls the `service_fun` call-back function
        with the inbound messages, then respond with the return value of the `service` function.
          :param subject: Subject that the service as a subscriber will observe.
          :param service_fun: a Callable function. Its return value will be the response.
        """

        async def nats_callback(msg):
            self.logger.debug(f"Call service function with '{msg}'")
            service_response = await service_fun(msg.data)
            self.logger.debug(f"Respont with '{service_response}'")
            if service_response is None:
                service_response = b""
            # await msg.respond(service_response)
            await self.nats_conn.publish(subject=msg.reply, payload=service_response)

        subscription = await self.nats_conn.subscribe(subject=subject, cb=nats_callback)
        self.logger.debug(f"subscription type: {type(subscription)}")
        subs = Subscriber(self.nats_conn, subscription)
        self.logger.debug(f"Subscribed to {subject} via subscriber: {subs}")
        return subs

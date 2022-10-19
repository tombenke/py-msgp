"""The NATS/NATS-Streaming implementation of the Messeger class"""
import asyncio
from typing import Callable, Optional
from loguru import logger
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN
from messenger import messenger
from messenger import subscriber
from nats_messenger.subscriber import Subscriber

DEFAULT_CONNECT_TIMEOUT = 2  # in seconds
DEFAULT_RECONNECT_TIME_WAIT = 2  # in seconds
DEFAULT_MAX_RECONNECT_ATTEMPTS = 60
DEFAULT_PING_INTERVAL = 120  # in seconds
DEFAULT_MAX_OUTSTANDING_PINGS = 2
DEFAULT_MAX_FLUSHER_QUEUE_SIZE = 1024
DEFAULT_DRAIN_TIMEOUT = 30  # in seconds


class Messenger(messenger.Messenger):
    """
    The Messenger class that provides the implementation of the generic messaging pattern methods
    defined by the `messenger.Messenger` absctract class.
    This implementation uses the NATS and NATS streaming messaging middleware.

    Args:
      url (str): The server's URL
      credentials (str): The server credentials
      cluster_id: The cluter ID of the server
      client_id: The client ID of the connecting client
      _logger:
      error_cb:
      disconnected_cb:
      closed_cb:
      discovered_server_cb:
      reconnected_cb:
      name:
      pedantic:
      verbose:
      allow_reconnect:
      connect_timeout:
      reconnect_time_wait:
      max_reconnect_attempts:
      ping_interval:
      max_outstanding_pings:
      dont_randomize:
      flusher_queue_size:
      no_echo:
      tls:
      tls_hostname:
      user:
      password:
      token:
      drain_timeout:
      signature_cb:
      user_jwt_cb:
      user_credentials:
      nkeys_seed:
    """

    def __init__(
        self,
        url: str,
        credentials: str,
        cluster_id: str,
        client_id: str,
        _logger=logger,
        error_cb=None,
        disconnected_cb=None,
        closed_cb=None,
        discovered_server_cb=None,
        reconnected_cb=None,
        name=None,
        pedantic=False,
        verbose=False,
        allow_reconnect=True,
        connect_timeout=DEFAULT_CONNECT_TIMEOUT,
        reconnect_time_wait=DEFAULT_RECONNECT_TIME_WAIT,
        max_reconnect_attempts=DEFAULT_MAX_RECONNECT_ATTEMPTS,
        ping_interval=DEFAULT_PING_INTERVAL,
        max_outstanding_pings=DEFAULT_MAX_OUTSTANDING_PINGS,
        dont_randomize=False,
        flusher_queue_size=DEFAULT_MAX_FLUSHER_QUEUE_SIZE,
        no_echo=False,
        tls=None,
        tls_hostname=None,
        user=None,
        password=None,
        token=None,
        drain_timeout=DEFAULT_DRAIN_TIMEOUT,
        signature_cb=None,
        user_jwt_cb=None,
        user_credentials=None,
        nkeys_seed=None,
    ):
        """
        Constructor for a Messenger
        """

        self.url = url
        self.credentials = credentials
        self.cluster_id = cluster_id
        self.client_id = client_id
        self.logger = _logger
        self.error_cb = error_cb
        self.disconnected_cb = disconnected_cb
        self.closed_cb = closed_cb
        self.discovered_server_cb = discovered_server_cb
        self.reconnected_cb = reconnected_cb
        self.name = name
        self.pedantic = pedantic
        self.verbose = verbose
        self.allow_reconnect = allow_reconnect
        self.connect_timeout = connect_timeout
        self.reconnect_time_wait = reconnect_time_wait
        self.max_reconnect_attempts = max_reconnect_attempts
        self.ping_interval = ping_interval
        self.max_outstanding_pings = max_outstanding_pings
        self.dont_randomize = dont_randomize
        self.flusher_queue_size = flusher_queue_size
        self.no_echo = no_echo
        self.tls = tls
        self.tls_hostname = tls_hostname
        self.user = user
        self.password = password
        self.token = token
        self.drain_timeout = drain_timeout
        self.signature_cb = signature_cb
        self.user_jwt_cb = user_jwt_cb
        self.user_credentials = user_credentials
        self.nkeys_seed = nkeys_seed

        self.nats_conn: NATS
        self.stan_conn: STAN

    async def open(self):
        """
        Opens the connection to the messaging middleware
        """

        # Use borrowed connection for NATS then mount NATS Streaming
        # client on top.
        self.logger.debug(f"Connect to NATS at '{self.url}'")
        self.nats_conn = NATS()
        await self.nats_conn.connect(
            servers=self.url,
            io_loop=asyncio.get_event_loop(),
            error_cb=self.error_cb,
            disconnected_cb=self.disconnected_cb,
            closed_cb=self.closed_cb,
            discovered_server_cb=self.discovered_server_cb,
            reconnected_cb=self.reconnected_cb,
            name=self.name,
            pedantic=self.pedantic,
            verbose=self.verbose,
            allow_reconnect=self.allow_reconnect,
            connect_timeout=self.connect_timeout,
            reconnect_time_wait=self.reconnect_time_wait,
            max_reconnect_attempts=self.max_reconnect_attempts,
            ping_interval=self.ping_interval,
            max_outstanding_pings=self.max_outstanding_pings,
            dont_randomize=self.dont_randomize,
            flusher_queue_size=self.flusher_queue_size,
            no_echo=self.no_echo,
            tls=self.tls,
            tls_hostname=self.tls_hostname,
            user=self.user,
            password=self.password,
            token=self.token,
            drain_timeout=self.drain_timeout,
            signature_cb=self.signature_cb,
            user_jwt_cb=self.user_jwt_cb,
            user_credentials=self.user_credentials,
            nkeys_seed=self.nkeys_seed,
        )

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

    async def publish(
        self, subject: str, payload: bytes, headers: Optional[dict] = None
    ):
        """
        Publishes `payload` message to the `subject` topic

        Args:
          subject: Subject to which the message will be published.
          payload: Message data.
          headers: Dictionary with key-value pairs, that carry meta information on the payload.
        """
        self.logger.debug(f"Publish to {subject} the payload '{payload}'")
        await self.nats_conn.publish(subject=subject, payload=payload)

    async def subscribe(
        self, subject: str, callback: Callable[[bytes], None]
    ) -> subscriber.Subscriber:
        """
        Subscribes to the `subject` topic, and calls the `callback` function with the inbound messages
        so the messages will be processed asychronously.

        Args:
          subject: Subject that the subscriber will observe.
          callback: a Callable function, that the subscriber will call.
        """

        async def nats_callback(msg):
            self.logger.debug(f"Subscription callback function is called with '{msg}'")
            await callback(msg.data)

        subscription = await self.nats_conn.subscribe(subject=subject, cb=nats_callback)
        subs = Subscriber(self.nats_conn, subscription)
        self.logger.debug(f"Subscribed to {subject} via subscriber: {subs}")
        return subs

    async def request(
        self,
        subject: str,
        payload: bytes,
        timeout: float,
        headers: Optional[dict] = None,
    ):
        """
        Send `payload` as a request message through the `subject` topic and expects a response until `timeout`.
        Returns with a future that is the response.

        Args:
          subject: Subject to which the request will be sent.
          payload: Message data.
          timeout: Timeout in seconds, until the request waits for the response.
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

        Args:
          subject: Subject that the service as a subscriber will observe.
          service_fun: a Callable function. Its return value will be the response.
        """

        async def nats_callback(msg):
            self.logger.debug(f"Call service function with '{msg}'")
            service_response = await service_fun(msg.data)
            self.logger.debug(f"Respond with '{service_response}'")
            if service_response is None:
                service_response = b""
            # await msg.respond(service_response)
            await self.nats_conn.publish(subject=msg.reply, payload=service_response)

        subscription = await self.nats_conn.subscribe(subject=subject, cb=nats_callback)
        subs = Subscriber(self.nats_conn, subscription)
        self.logger.debug(f"Subscribed to {subject} via subscriber: {subs}")
        return subs

    # Functions for durable subjects
    async def publish_durable(
        self, subject: str, payload: bytes, headers: Optional[dict] = None
    ):
        """
        Publishes `data` to the cluster into the `subject` and wait for an ACK.

        Args:
          subject: Subject that the subscriber will observe.
          payload: Message data.
          headers: Dictionary with key-value pairs, that carry meta information on the payload.
        """
        self.logger.debug(f"Publish to {subject} the payload '{payload}'")
        await self.stan_conn.publish(subject=subject, payload=payload)

    async def publish_async_durable(
        self,
        subject: str,
        payload: bytes,
        ack_handler: Callable[[bool], None],
        headers: Optional[dict] = None,
    ):
        """
        Publishes the `payload` to the `subject` topic and
        asynchronously process the ACK or error state via the `ack_handler` callback function.

        Args:
          subject: Subject that the subscriber will observe.
          payload: Message data.
          ack_handler: Callback function for acknowledge handling.
          headers: Dictionary with key-value pairs, that carry meta information on the payload.
        """
        self.logger.debug(
            f"Publish to {subject} the payload '{payload}' asynchronously"
        )
        await self.stan_conn.publish(
            subject=subject, payload=payload, ack_handler=ack_handler
        )

    async def subscribe_durable(self, subject: str, callback: Callable[[bytes], None]):
        """
        Subscribes to the durable `subject`, and call `callback` with the received content.
        Automatically acknowledges to the subject the take-over of the message.

        Args:
          subject: Subject that the subscriber will observe.
          callback: a Callable function, that the subscriber will call.
        """

        async def stan_callback(msg):
            self.logger.debug(f"Subscription callback function is called with '{msg}'")
            await callback(msg.data)

        subscription = await self.stan_conn.subscribe(subject=subject, cb=stan_callback)
        subs = Subscriber(self.stan_conn, subscription)
        self.logger.debug(f"Subscribed to {subject} via subscriber: {subs}")
        return subs

    async def subscribe_durable_with_ack(
        self, subject: str, callback: Callable[[bytes], None]
    ):
        """
        Subscribes to the durable `subject`, and call `callback` with the received content.
        The second argument of the `service_fun` callback is the acknowledge callback function,
        that has to be called by the consumer of the content.

        Args:
          subject: Subject that the subscriber will observe.
          callback: a Callable function, that the subscriber will call.
        """

        async def stan_callback(msg):
            self.logger.debug(f"Subscription callback function is called with '{msg}'")
            acknowledge = await callback(msg.data)
            if acknowledge:
                await self.stan_conn.ack(msg)
                self.logger.debug(f"message {msg.sequence}, is acknowledged")
            else:
                self.logger.debug(f"message {msg.sequence}, is NOT acknowledged")

        subscription = await self.stan_conn.subscribe(
            subject=subject,
            cb=stan_callback,
            start_at="new_only",
            durable_name="durable",
            deliver_all_available=False,
            manual_acks=True,
        )
        subs = Subscriber(self.stan_conn, subscription)
        self.logger.debug(f"Subscribed to {subject} via subscriber: {subs}")
        return subs

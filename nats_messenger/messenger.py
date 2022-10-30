"""The NATS/NATS-Streaming implementation of the Messeger class"""
from typing import Callable, Optional, List
from loguru import logger
import nats
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
DEFAULT_INBOX_PREFIX = b"_INBOX"
DEFAULT_PENDING_SIZE = 2097152


class Messenger(messenger.Messenger):
    """
    The Messenger class that provides the implementation of the generic messaging pattern methods
    defined by the `messenger.Messenger` absctract class.
    This implementation uses the NATS/JetStream messaging middleware.

    Args:
    """

    nats_conn = None
    js_conn = None

    def __init__(
        self,
        url: str,
        # credentials: str,
        # cluster_id: str,
        # client_id: str,
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
        inbox_prefix=DEFAULT_INBOX_PREFIX,
        pending_size=DEFAULT_PENDING_SIZE,
        flush_timeout=None,
    ):
        """
        Constructor for a Messenger
        """

        self.url = url
        # self.credentials = credentials
        # self.cluster_id = cluster_id
        # self.client_id = client_id
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
        self.inbox_prefix = inbox_prefix
        self.pending_size = pending_size
        self.flush_timeout = flush_timeout

    async def open(self):
        """
        Opens the connection to the messaging middleware
        """

        # Use borrowed connection for NATS then mount NATS Streaming
        # client on top.
        self.logger.debug(f"Connect to NATS at '{self.url}'")
        self.nats_conn = await nats.connect(
            servers=self.url,
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
            inbox_prefix=self.inbox_prefix,
            pending_size=self.pending_size,
            flush_timeout=self.flush_timeout,
        )
        self.js_conn = self.nats_conn.jetstream()

    async def close(self):
        """
        Closes the connection to the messaging middleware
        """

        # We are using a NATS borrowed connection so we need to close manually.
        self.logger.debug("Close to NATS")
        await self.nats_conn.drain()
        # await self.nats_conn.close()

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
        await self.nats_conn.publish(subject=subject, payload=payload, headers=headers)

    async def subscribe(
        self, subject: str, callback: Callable[[bytes, dict], None]
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
            await callback(msg.data, msg.headers)

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
    ) -> tuple[bytes, dict]:
        """
        Send `payload` as a request message through the `subject` topic and expects a response until `timeout`.
        Returns with a future that is the response.

        Args:
          subject: Subject to which the request will be sent.
          payload: Message data.
          timeout: Timeout in seconds, until the request waits for the response.
          headers: The key-value pairs of the request headers

        Return:
          - payload: The payload of the response
          - headers: The key-value pairs of the response headers
        """
        self.logger.debug(f"Send request {subject} with payload '{payload}'")
        response = await self.nats_conn.request(
            subject=subject, payload=payload, timeout=timeout, headers=headers
        )
        self.logger.debug(f"got response {response}")
        return response.data, response.headers

    async def response(
        self, subject: str, service_fun: Callable[[bytes, dict], tuple[bytes, dict]]
    ):
        """
        Subscribes to the `subject` topic, and calls the `service_fun` call-back function
        with the inbound messages, then respond with the return value of the `service` function.

        Args:
          subject: Subject that the service as a subscriber will observe.
          service_fun: a Callable function. Its return value will be the response.
        """

        async def nats_callback(msg):
            self.logger.debug(f"Call service function with '{msg}'")
            service_response, service_response_headers = await service_fun(
                msg.data, msg.headers
            )
            self.logger.debug(
                f"Respond with payload: '{service_response}', headers: {service_response_headers}"
            )
            if service_response is None:
                service_response = b""
            await self.nats_conn.publish(
                subject=msg.reply,
                payload=service_response,
                headers=service_response_headers,
            )

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
        await self.js_conn.publish(subject=subject, payload=payload, headers=headers)

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
        ack = await self.js_conn.publish(
            subject=subject, payload=payload, headers=headers
        )
        self.logger.debug(f"Publish to {subject} acknowledged with: {ack}")
        await ack_handler(True)

    async def subscribe_durable(
        self, subject: str, callback: Callable[[bytes, dict], None]
    ):
        """
        Subscribes to the durable `subject`, and call `callback` with the received content.
        Automatically acknowledges to the subject the take-over of the message.

        Args:
          subject: Subject that the subscriber will observe.
          callback: a Callable function, that the subscriber will call.
        """

        async def js_callback(msg):
            self.logger.debug(f"Subscription callback function is called with '{msg}'")
            await callback(msg.data, msg.headers)

        subscription = await self.js_conn.subscribe(
            subject, cb=js_callback, manual_ack=False
        )
        subs = Subscriber(self.js_conn, subscription)
        self.logger.debug(f"Subscribed to {subject} via subscriber: {subs}")
        return subs

    async def subscribe_durable_with_ack(
        self, subject: str, callback: Callable[[bytes, dict], None]
    ):
        """
        Subscribes to the durable `subject`, and call `callback` with the received content.
        The callback must return the content, or None if it failed.

        Args:
          subject: Subject that the subscriber will observe.
          callback: a Callable function, that the subscriber will call.
        """

        async def js_callback(msg):
            self.logger.debug(f"Subscription callback function is called with '{msg}'")
            acknowledge = await callback(msg.data, msg.headers)
            if acknowledge is None:
                await msg.nak()
                self.logger.debug(f"message {msg}, is NOT acknowledged")
            else:
                await msg.ack()
                self.logger.debug(f"message {msg}, is acknowledged")

        subscription = await self.js_conn.subscribe(
            subject=subject,
            cb=js_callback,
            manual_ack=True,
        )
        subs = Subscriber(self.js_conn, subscription)
        self.logger.debug(f"Subscribed to {subject} via subscriber: {subs}")
        return subs

    async def add_stream(self, name: str, subjects: List[str]):
        """
        Add a Stream
        """
        return await self.js_conn.add_stream(name=name, subjects=subjects)

    async def delete_stream(self, name: str):
        """
        Delete a Stream
        """
        return await self.js_conn.delete_stream(name)

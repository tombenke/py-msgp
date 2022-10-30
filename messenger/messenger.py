"""The Messenger class"""
from abc import ABC, abstractmethod
from typing import Callable, Optional
from .subscriber import Subscriber


class Messenger(ABC):
    """
    Abstract base class for the Messenger class that provides the generic messaging pattern methods.
    The real messenger classes must implement the abstract methods
    """

    @abstractmethod
    async def open(self):
        """
        Opens the connection to the messaging middleware
        """

    @abstractmethod
    async def close(self):
        """
        Closes the connection to the messaging middleware
        """

    # Functions for non durable subjects
    @abstractmethod
    async def publish(self, subject: str, payload: bytes, headers: Optional[dict]):
        """
        Publishes `payload` message to the `subject` topic

        Args:
          subject (str): Subject to which the message will be published.
          payload (bytes): Message data.
          headers (Optional[dict]): Dictionary with key-value pairs, that carry meta information on the payload.
        """

    @abstractmethod
    async def subscribe(
        self, subject: str, callback: Callable[[bytes, dict], None]
    ) -> Subscriber:
        """
        Subscribes to the `subject` topic, and calls the `callback` function with the inbound messages
        so the messages will be processed asychronously.

        Args:
          subject: Subject that the subscriber will observe.
          callback: a Callable function, that the subscriber will call.
        """

    @abstractmethod
    async def request(
        self, subject: str, payload: bytes, timeout: float, headers: Optional[dict]
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

    @abstractmethod
    async def response(self, subject: str, service_fun: Callable[[bytes, dict], None]):
        """
        Subscribes to the `subject` topic, and calls the `service_fun` call-back function
        with the inbound messages, then respond with the return value of the `service` function.

        Args:
          subject: Subject that the service as a subscriber will observe.
          service_fun: a Callable function. Its return value will be the response.
        """

    # Functions for durable subjects
    @abstractmethod
    async def publish_durable(
        self, subject: str, payload: bytes, headers: Optional[dict]
    ):
        """
        Publishes `data` to the cluster into the `subject` and wait for an ACK.

        Args:
          subject: Subject that the subscriber will observe.
          payload: Message data.
          headers: Dictionary with key-value pairs, that carry meta information on the payload.
        """

    @abstractmethod
    async def publish_async_durable(
        self,
        subject: str,
        payload: bytes,
        ack_handler: Callable[[bool], None],
        headers: Optional[dict],
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

    @abstractmethod
    async def subscribe_durable(self, subject: str, callback: Callable[[bytes], None]):
        """
        Subscribes to the durable `subject`, and call `callback` with the received content.
        Automatically acknowledges to the subject the take-over of the message.

        Args:
          subject: Subject that the subscriber will observe.
          callback: a Callable function, that the subscriber will call.
        """

    @abstractmethod
    async def subscribe_durable_with_ack(
        self, subject: str, callback: Callable[[bytes, Callable[[], bool]], None]
    ):
        """
        Subscribes to the durable `subject`, and call `callback` with the received content.
        The second argument of the `callback` callback is the acknowledge callback function,
        that has to be called by the consumer of the content.

        Args:
          subject: Subject that the subscriber will observe.
          callback: a Callable function, that the subscriber will call.
        """

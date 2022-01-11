"""The Messenger class"""
from abc import ABC, abstractmethod
from typing import Callable
from messenger.subscriber import Subscriber


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

    @abstractmethod
    async def publish(self, subject: str, payload: bytes):
        """
        Publishes `payload` message to the `subject` topic
          :param subject: Subject to which the message will be published.
          :param payload: Message data.
        """

    @abstractmethod
    async def subscribe(
        self, subject: str, callback: Callable[[bytes], None]
    ) -> Subscriber:
        """
        Subscribes to the `subject` topic, and calls the `callback` function with the inbound messages
        so the messages will be processed asychronously.
          :param subject: Subject that the subscriber will observe.
          :param callback: a Callable function, that the subscriber will call.
        """

    @abstractmethod
    async def request(self, subject: str, payload: bytes, timeout: float):
        """
        Send `payload` as a request message through the `subject` topic and expects a response until `timeout`.
        Returns with a future that is the response.
          :param subject: Subject to which the request will be sent.
          :param payload: Message data.
          :param timeout: Timeout in seconds, until the request waits for the response.
        """

    @abstractmethod
    async def response(self, subject: str, service_fun: Callable[[bytes], None]):
        """
        Subscribes to the `subject` topic, and calls the `service_fun` call-back function
        with the inbound messages, then respond with the return value of the `service` function.
          :param subject: Subject that the service as a subscriber will observe.
          :param service_fun: a Callable function. Its return value will be the response.
        """

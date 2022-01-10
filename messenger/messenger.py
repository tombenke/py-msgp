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
        Subscribes to the `subject` topic, and calls the `cb` call-back function with the inbound messages
        so the messages will be processed asychronously.
        """

    # def request(self):
    # def response(self):

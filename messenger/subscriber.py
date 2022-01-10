"""The Subscriber class"""
from abc import ABC, abstractmethod


class Subscriber(ABC):
    """
    Abstract base class that represents a subscriber entity that observer a topic,
    and can unsubscribe from it.
    The real messenger classes must implement the abstract methods
    """

    def __str__(self):
        pass

    @abstractmethod
    async def unsubscribe(self):
        """Unsubscribes from the topic"""

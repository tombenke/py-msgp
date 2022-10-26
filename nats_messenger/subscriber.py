"""The Subscriber class"""
from messenger import subscriber


class Subscriber(subscriber.Subscriber):
    """
    Represents a subscriber entity that observes a topic, and can unsubscribe from it.
    """

    def __init__(self, client, subscription):
        """Constructor for the subscriber"""
        self.client = client
        self.subscription = subscription

    def __str__(self):
        return f"subscription:{self.subscription}"

    async def unsubscribe(self):
        """Unsubscribes from the topic"""
        if hasattr(self.subscription, "unsubscribe"):
            await self.subscription.unsubscribe()
        else:
            await self.client.unsubscribe()

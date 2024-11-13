from typing import Any
from typing import Callable
from collections import deque
from abc import ABC, abstractmethod

class Base(ABC):
    """
    An abstract base class for subscribers to a publisher.

    Subscribers are responsible for receiving messages, managing transactions,
    and closing their connections.
    """

    @abstractmethod
    def handle(self,topic: str, message: Any) -> None:
        """
        Receives a message from the publisher.

        Args:
            message: The message to be received.
        """

    @abstractmethod
    def begin(self) -> None:
        """
        Starts a new transaction.
        """

    @abstractmethod
    def commit(self) -> None:
        """
        Commits the current transaction.
        """

    @abstractmethod
    def rollback(self) -> None:
        """
        Rolls back the current transaction.
        """

    @abstractmethod
    def close(self) -> None:
        """
        Closes the subscriber and its connection.
        """

class Subscriber(Base):
    def __init__(self):
        self.handlers = dict[str, list[Callable]]()
        self.queue = deque[tuple[str, Any]]()

    def subscribe(self, topic: str, handler: Callable):
        self.handlers.setdefault(topic, []).append(handler)

    def handle(self, topic: str, message: Any):
        self.queue.append((topic, message))

    def commit(self):
        while self.queue:
            topic, message = self.queue.popleft()
            [handler(message) for handler in self.handlers.get(topic, [])]

    def rollback(self):
        self.queue.clear()

    def begin(self):
        [handler('begin', None) for handler in self.handlers.get('begin', [])]

    def close(self):
        [handler('begin', None) for handler in self.handlers.get('close', [])]


class Publisher:
    """
    A publisher that manages a set of subscribers and publishes messages to them.

    The publisher is responsible for subscribing and unsubscribing subscribers,
    publishing messages to subscribed topics, and coordinating transactions
    across all subscribers.

    The difference between a publisher and a message bus is that a publisher
    is responsible for publish data from the inside of the bounded context
    to outside systems. A message bus is responsible for routing events and
    commands within the bounded context.
    """

    def __init__(self) -> None:
        """
        Initializes the publisher with an empty subscriber dictionary.
        """
        self.subscribers = list[Subscriber]()

    def subscribe(self, subscriber: Subscriber) -> None:
        """
        Subscribes a new subscriber to the publisher.

        Parameters:
            subscriber: The subscriber to subscribe.
        """
        assert isinstance(subscriber, Base), 'Subscriber should inherit from Base'
        self.subscribers.append(subscriber)

    def publish(self, topic: str, message: Any) -> None:
        """
        Publishes a message to a specific topic.

        The message is sent to all subscribers of the given topic.

        Parameters:
            topic: The topic to publish to.
            message: The message to be published.
        """
        [subscriber.handle(topic, message) for subscriber in self.subscribers]

    def commit(self) -> None:
        """
        Commits the current transaction for all subscribers.
        """
        [subscriber.commit() for subscriber in self.subscribers]
            

    def rollback(self) -> None:
        """
        Rolls back the current transaction for all subscribers.
        """
        [subscriber.rollback() for subscriber in self.subscribers]


    def begin(self) -> None:
        """
        Starts a new transaction for all subscribers.
        """
        [subscriber.begin() for subscriber in self.subscribers]

    def close(self) -> None:
        """
        Closes all subscribers and their connections.
        """
        [subscriber.close() for subscriber in self.subscribers]
from typing import Any
from typing import Callable
from datetime import datetime, timezone
from collections import deque
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class Message[T]:
    '''
    A generic message to be published by the publisher.

    Attributes:
        sender: The identifier of the entitiy that sends the message.
        payload: The payload of the message.
    '''
    sender: str
    payload: T
    timestamp: datetime = datetime.now(timezone.utc)


class Base(ABC):
    """
    An abstract base class for a publisher.

    A publisher is responsible for publishing messages to external systems
    using callable subscribers. It should implement the methods to mantain 
    transacional consistency and resource management using the begin, commit,
    rollback and close methods.

    
    The difference between a publisher and a messagebus is that a publisher
    is responsible for publish data from the inside of the bounded context
    to outside systems. A message bus is responsible for routing events and
    commands within the bounded context, and handle them inside a transaction.

    Messages passed to the publisher should be serializable objects.
    """

    @abstractmethod
    def publish(self, topic: str, message: Message) -> None:
        """
        Publishes a message to a topic.

        Args:
            message: The message to be published.
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

class Publisher(Base):
    '''
    An in memory publisher using a simple queue as buffer for messages.
    '''

    def __init__(self):
        self.subscribers = dict[str, list[Callable]]()
        self.queue = deque[tuple[str, Any]]()

    def subscribe(self, topic: str, subscriber: Callable):
        '''
        Subscribes a new handler to a topic. Each topic can have multiple
        subscribers.

        Parameters:
            topic: The topic to subscribe to.
            handler: The handler to subscribe.
        '''
        self.subscribers.setdefault(topic, []).append(subscriber)

    def publish(self, topic: str, message: Message):
        '''
        Receives a message from the publisher. 
        '''
        self.queue.append((topic, message))

    def commit(self):
        '''
        Commit all messages enqueued to their respective subscribers.
        '''
        while self.queue:
            topic, message = self.queue.popleft()
            [subscriber(message) for subscriber in self.subscribers.get(topic, [])]

    def rollback(self):
        '''
        Rollback all messages enqueued.        
        '''
        self.queue.clear()

    def begin(self):
        '''
        Begin a new transaction.
        '''
        [subscriber(None) for subscriber in self.subscribers.get('begin', [])]

    def close(self):
        [subscriber(None) for subscriber in self.subscribers.get('close', [])]
        self.queue.clear()
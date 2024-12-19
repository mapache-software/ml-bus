from abc import ABC, abstractmethod
from uuid import uuid4, UUID
from typing import Any
from typing import Callable
from datetime import datetime, timezone
from collections import deque
from dataclasses import dataclass, field
from fast_depends import inject as _inject
from fast_depends import Provider as _Provider

@dataclass
class Message[T]:
    '''
    A generic message to be published by the publisher. The difference between
    a message and events or commands is that messages are mean to be published
    to external systems, while events and commands are mean to be published
    and handled inside the bounded context.

    Attributes:
        payload: The payload of the message.
        sender: The identifier of the entity that sends the message.
        id: A unique identifier for the message.
        headers: Optional headers for the message.
        timestamp: The timestamp of the message creation.
    '''
    payload: T
    sender: Any = field(default=None)
    id: UUID = field(default_factory=uuid4)
    headers: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class Base(ABC):
    """
    An abstract base class for a publisher.

    A publisher is responsible for publishing messages to external systems
    using callable subscribers. Implementations of this class should ensure
    transactional consistency and proper resource management by providing
    concrete definitions for the `begin`, `commit`, `rollback`, and `close`
    methods.
    
    The key distinction between a publisher and a message bus is:
    - **Publisher**: Sends data from within a bounded context to external systems.
    - **Message Bus**: Routes events and commands within the bounded context
      and ensures they are handled within a transaction.

    Messages passed to the publisher should be serializable objects, such as strings,
    dictionaries, or JSON-encoded data.
    
    Methods:
    - `publish`: Publishes a message to a specified topic.
    - `begin`: Starts a new transaction.
    - `commit`: Commits the current transaction to persist changes.
    - `rollback`: Rolls back the current transaction to its previous state.
    - `close`: Closes the publisher, releasing resources and connections.
    """

    @abstractmethod
    def publish(self, topic: str, message: Message) -> None:

        """
        Publishes a message to a specific topic.

        This method should be implemented by a concrete subclass to define the
        logic for publishing messages to the external system (e.g., a message queue,
        a Kafka topic, or an HTTP endpoint).

        Args:
            `topic` (str): The topic, channel, or queue to which the message should be published.
            `message` (Any): The message to be published. The message should be a serializable 
                           object (e.g., string, dictionary, or JSON).

        Raises:
            Exception: If an error occurs during publishing. Subclasses should specify the
                       exact type of exception raised.
        """

    def begin(self) -> None:
        """
        Starts a new transaction. Override this method with your own logic.

        This method is used to indicate the beginning of a transactional context.
        Concrete implementations should manage any resources necessary to track the transaction.
        """
        pass

    def commit(self) -> None:
        """
        Commits the current transaction. Override this method with your own logic.

        This method finalizes the transaction, persisting any changes made during
        the transactional context. Implementations should handle the logic to commit changes
        to the external system.
        """
        pass

    def rollback(self) -> None:
        """        
        Rolls back the current transaction. Override this method with your own logic.

        If an error occurs during the transaction, this method reverts changes to
        the previous consistent state. Implementations should handle cleanup and
        ensure the system remains consistent.
        """
        pass

    def close(self) -> None:
        """
        Closes the publisher and releases any resources or connections. Override this method with your own logic.

        This method should ensure that all open connections, file handles, or other
        resources are properly closed to avoid memory leaks or resource contention.
        """
        pass


class Publisher(Base):
    '''
    An in-memory publisher that uses a simple queue as a buffer for messages. 
    This class allows registering subscribers for specific topics and supports 
    message publishing with commit and rollback capabilities.

        Example:
        publisher = Publisher()

        @publisher.subscribe('first-topic', 'second-topic')
        def subscriber(message: Message[str], dependency: DependencyType = Depends(some_dependency)):
            print(f"received {message.payload} from {message.sender}")

        publisher.publish('first-topic', Message(sender='me', payload='hello'))
        publisher.rollback()
        publisher.publish('first-topic', Message(sender='me', payload='hello, last message wasn't delivered!'))
        publisher.commit() # prints "received hello, last message wasn't delivered! from me"
    '''

    def __init__(self):
        self.provider = _Provider()
        self.subscribers = dict[str, list[Callable]]()
        self.queue = deque[tuple[str, Any]]()

    @property
    def dependency_overrides(self) -> dict[Callable[..., Any], Callable[..., Any]]:
        return self.provider.dependency_overrides

    def add_subscriber(self, topic: str, subscriber: Callable):
        '''
        Adds a new subscriber to the publisher. Each subscriber is a callable
        that receives a message as argument. 

        Parameters:
            `topic`: The topic to subscribe to.
            `subscriber`: The subscriber to add.
        '''
        subscriber_with_inject = _inject(dependency_overrides_provider=self.provider)(subscriber)
        self.subscribers.setdefault(topic, []).append(subscriber_with_inject)

    def subscribe(self, *topics: str):
        '''
        A decorator that adds a new subscriber to the publisher.
        
        Parameters:
            `topic`: The topic to subscribe to.

        Example:
        publisher = Publisher()

        @publisher.subscribe('first-topic', 'second-topic')
        def subscriber(message: Message[str], dependency: DependencyType = Depends(some_dependency)):
            print(f"received {message.payload} from {message.sender}")

        publisher.publish('first-topic', Message(sender='me', payload='hello'))
        '''

        def decorator(subscriber: Callable):
            subscriber_with_inject = _inject(dependency_overrides_provider=self.provider)(subscriber)
            for topic in topics:
                self.subscribers.setdefault(topic, []).append(subscriber_with_inject)
            return subscriber
        return decorator

    def publish(self, topic: str, message: Message):
        '''
        Publishes a message to a specified topic. The message is added to a simple queue 
        and will be delivered to subscribers when `commit` is called.

        Parameters:
            `topic` (str): The topic to which the message should be published.
            `message` (Message): The message to be delivered.
        '''
        self.queue.append((topic, message))

    def commit(self):
        '''
        Delivers all enqueued messages to their respective subscribers. 
        Each message is processed in the order it was published.
        '''
        while self.queue:
            topic, message = self.queue.popleft()
            for subscriber in self.subscribers.get(topic, []):
                subscriber(message)

    def rollback(self):
        '''
        Clears all enqueued messages without delivering them to subscribers. 
        This undoes all pending publish operations.
        '''
        self.queue.clear()
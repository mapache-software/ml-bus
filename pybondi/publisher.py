from typing import Callable
from typing import Any
from fast_depends import Provider
from fast_depends import inject
from fast_depends import Depends as Depends

class Message:
    """
    Represents a base class for messages. Messages are objects that should be
    used to communicate data to components to the outside world.

    This class is intended to be subclassed to define concrete message types
    with the required attributes.
    """

class Publisher:
    """
    Represents a base class for publishers. Publishers are objects that should
    be used to publish messages to subscribers.

    Pydantic validation is performed on the type of the message if a type hint
    is provided. Dependency injection is supported for subscribers.

    Attributes:
        subscribers: A dictionary that maps topics to a set of subscribers
            that are interested in messages published to that topic.

    Methods:
        subscribe: A decorator that can be used to subscribe a callback to a
            topic. The callback will be called when a message is published to
            the topic.
        publish: Publishes a message to all subscribers

    Example:
        .. code-block:: python

        from pybondi import Depends
        from pybondi import Publisher

        publisher = Publisher()
        db = []

        def get_db(): # Define dependencies like in FastAPI
            return db
        
        @publisher.subscriber('topic-1', 'topic-2')
        def callback(message):
            print(message)

        @publisher.subscriber('topic-2')
        def second_callback(message, db = Depends(get_db)): # Dependency injection can be used
            print(message)
            db.append(message)
            
        publisher.publish('topic-2', 'Hello world!') # Will print 'Hello world!' twice
        print(db) # Will print ['Hello world!']
    """
    def __init__(self, provider: Provider = None, cast_dependency: bool = True):
        """
        Args:
            provider (Provider, optional): A provider instance to use for dependency injection. Defaults to None.
            cast_dependency (bool, optional): Whether to cast the dependencies to the expected type. Defaults to True.
        """
        self.cast_dependency = cast_dependency
        self.provider = provider or Provider()
        self.subscribers = dict[str, set[Callable[[Message | Any], None]]]()

    def subscriber(self, *topics: str):
        '''
        A decorator that can be used to subscribe a callback to a topic. 
        The callback will be called when a message is published to the topic.

        Args:
            *topics: The topics to subscribe to.

        Returns:
            A decorator that can be used to subscribe a callback to a topic.
        '''
        def decorator(callback: Callable[[Message | Any], None]):
            for topic in topics:
                if topic not in self.subscribers:
                    self.subscribers[topic] = set()
                injected = inject(callback, dependency_overrides_provider=self.provider, cast=self.cast_dependency)
                self.subscribers[topic].add(injected)
            return callback
        return decorator
    
    def publish(self, topic: str, message: Message | Any):
        """
        Publishes a message to all subscribers. Can be a Message
        or any other object.

        Args:
            topic (str): The topic to publish the message to.
            message (Message | Any): The message to publish.
        """
        for callback in self.subscribers.get(topic, []):
            callback(message)
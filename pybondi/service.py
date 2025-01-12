from typing import Callable
from typing import Any
from fast_depends import Provider
from pybondi.publisher import Publisher, Message
from pybondi.commands import Commands, Command
from pybondi.events import Events, Event

class Service:
    """
    The Service class groups a Publisher, Commands and Events instances to provide a single interface for
    creating a service.

    Example:
        .. code-block:: python
    
        from pybondi import Service
        from pybondi import Depends

        service = Service()
        
        def some_dependency():
            raise NotImplementedError

        @service.handler
        def handle_some_cmd(command, dps = Depends(some_dependency)):
            ...

        @service.consumer
        def consume_some_event(event, dps = Depends(some_dependency)):
            ...

        @service.subscriber('topic-1', 'topic-2')
        def on_published(message, dps = Depends(some_dependency)):
            ...

        def concrete_dependency():
            return {}
            
        service.dependency_overrides[some_dependency] = concrete_dependency 
    """
    def __init__(self, key_generator: Callable[[str], str] = lambda name: name, provider: Provider = None, cast_dependency: bool = True):
        """
        Initializes a new instance of the Service class.

        Args:
            key_generator (Callable[[str], str], optional): A function that generates a key from a name. Defaults to lambda name: name.
            provider (Provider, optional): A provider instance to use for dependency injection. Defaults to None.
            cast_dependency (bool, optional): Whether to cast the dependencies to the expected type. Defaults to True.
        
        Notes:
            The key_generator function is used to generate a key from a name. This key is used to store the function in the commands and
            events maps. The default key_generator function simply returns the name unchanged. This is useful when you want to use some
            naming conventions like kebab-case or snake_case for the command and event names.
        """

        self.provider = provider or Provider()
        self.publisher = Publisher(self.provider, cast_dependency)
        self.commands = Commands(key_generator, self.provider, cast_dependency)
        self.events = Events(key_generator, self.provider, cast_dependency)

    @property
    def dependency_overrides(self):
        return self.provider.dependency_overrides
    
    def handle(self, command: Command) -> None:
        """
        Handles a command by invoking its associated handler.

        Args:
            command (Command): The command to handle.

        Raises:
            KeyError: If no handler is found for the command's key.
        """
        return self.commands.handle(command)

    def consume(self, event: Event) -> None:
        """
        Consumes an event by invoking its registered consumer functions.

        Args:
            event (Event): The event to consume.
        """
        return self.events.consume(event)
    
    def publish(self, topic: str, message: Message) -> None:
        """
        Publishes a message to a topic.

        Args:
            topic (str): The topic to publish the message to.
            message (Message): The message to publish.
        """
        return self.publisher.publish(topic, message)   

    def handler(self, wrapped: Callable[[Command], Any]):
        """
        Decorator to register a handler function for one or more command types.

        Args:
            wrapped (Callable[[Command], Any]): The handler function to register.

        Returns:
            Callable: The original handler function, unmodified.

        Notes:
            If the handler function is annotated with a union of command types,
            all of those types will be registered with the same handler.
        """
        return self.commands.handler(wrapped)
    
    def consumer(self, wrapped: Callable[[Event], Any]):
        """
        Decorator for registering a consumer function for one or more event types.

        Args:
            wrapped (Callable[[Event], Any]): The consumer function to register.

        Returns:
            Callable: The original handler function, unmodified.

        Note:
            If the handler function is annotated with a union of event types,
            all of those types will be registered with the same consumer.    
        """
        return self.events.consumer(wrapped)
    
    def subscriber(self, *topics: str):
        '''
        A decorator that can be used to subscribe a callback to a topic. 
        The callback will be called when a message is published to the topic.

        Args:
            *topics: The topics to subscribe to.

        Returns:
            A decorator that can be used to subscribe a callback to a topic.
        '''
        return self.publisher.subscriber(*topics)
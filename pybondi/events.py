from typing import Callable
from typing import Any
from inspect import signature

from fast_depends import Provider
from fast_depends import inject

class Event:
    """
    Represents a base class for events. Events are objects that encapsulate
    the data associated with a specific occurrence or notification.

    This class is intended to be subclassed to define concrete event types
    with the required attributes.
    """
    ...

class Events:
    """
    Manages the registration and handling of events and their associated consumers.

    Attributes:
        key_generator (Callable[[str], str]): A function used to generate keys for events 
            based on their class names. Defaults to an identity function.
        types (dict[str, type[Event]]): A dictionary mapping event keys to their types.
        consumers (dict[str, set[Callable[[Event], None]]]): A dictionary mapping event keys 
            to a set of consumer functions.

    Methods:
        consume(event: Event) -> None:
            Consumes an event by invoking its registered consumer functions.

        register(event_type: type[Event], consumer: Callable[[Event], None]) -> None:
            Registers an event type and its corresponding consumer function.

        consumer(wrapped: Callable[[Event], Any]) -> Callable:
            Decorator for registering a consumer function for one or more event types.


    Example:
        .. code-block:: python

        from dataclasses import dataclass
        from pybondi import Events

        events = Events()
        notifications = []  # List of notifications

        @dataclass
        class UserCreated(Event):
            id: str
            name: str

        @dataclass
        class UserUpdated(Event):
            id: str
            name: str

        @events.consumer
        def on_user_put(event: UserCreated | UserUpdated):
            notifications.append(event)

        @events.consumer
        def on_user_updated(event: UserUpdated):
            print(f"User {event.id} updated with name {event.name}")
        
        events.consume(UserCreated(id="1", name="Alice"))
        events.consume(UserUpdated(id="1", name="Bob")) # Output: User 1 updated with name Bob
        print(notifications)  # Output: [UserCreated(id='1', name='Alice'), UserUpdated(id='1', name='Bob')]
    """

    def __init__(self, key_generator: Callable[[str], str] = lambda name: name, provider: Provider = None, cast_dependency: bool = True):
        """
        Initializes the Events instance.

        Args:
            key_generator (Callable[[str], str], optional): A function to generate event keys 
                from class names. Defaults to a lambda returning the class name unchanged.
            provider (Provider, optional): A provider instance to use for dependency injection.
            cast_dependency (bool, optional): Whether to cast dependencies to the expected type.
        """
        self.cast_dependency = cast_dependency
        self.provider = provider or Provider()
        self.key_generator = key_generator
        self.types = dict[str, type[Event]]()
        self.consumers = dict[str, set[Callable[[Event], None]]]()

    def consume(self, event: Event) -> None:
        """
        Consumes an event by invoking its registered consumer functions.

        Args:
            event (Event): The event to consume.
        """
        key = self.key_generator(event.__class__.__name__)
        for consumer in self.consumers.get(key, set()):
            consumer(event)
    
    def register(self, event_type: type[Event], consumer: Callable[[Event], None]):
        """
        Registers an event type and its corresponding consumer function.

        Args:
            event_type (type[Event]): The type of the event to register.
            consumer (Callable[[Event], None]): The consumer function for the event.
        """


        key = self.key_generator(event_type.__name__)
        self.types[key] = event_type
        self.consumers.setdefault(key, set()).add(inject(consumer, dependency_overrides_provider=self.provider, cast=self.cast_dependency))

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
        function_signature = signature(wrapped)
        parameter = next(iter(function_signature.parameters.values()))
        if hasattr(parameter.annotation, '__args__'):
            for message_type in getattr(parameter.annotation, '__args__'):
                self.register(message_type, wrapped)
        else:
            message_type = parameter.annotation
            self.register(message_type, wrapped)
        return wrapped
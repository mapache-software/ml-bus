from abc import ABC, abstractmethod
from typing import Callable
from typing import Optional
from logging import getLogger
from collections import deque

logger = getLogger(__name__)

class Event(ABC):
    """
    An abstract base class for domain events. All events should inherit from this class, otherwise
    they will not be recognized by the message bus.
    """

class Command(ABC):
    """
    Command is a class representing a request to perform an action. All commands should inherit from this class.
    Otherwise, they will not be recognized by the message bus.
    """
    ...
    def execute(self):
        """
        Executes the command.
        """
        raise NotImplementedError

class Messagebus:
    """
    Messagebus is a class that routes domain events and commands to their respective handlers.

    Attributes:
        handlers: A dictionary mapping command types to their corresponding handlers.
        consumers: A dictionary mapping event types to a list of their consumers.
    """

    def __init__(self):
        self.command_handlers = dict[type[Command], Callable[[Command], None]]()
        self.event_handlers = dict[type[Event], list[Callable[[Event], None]]]()

    def subscribe(self, *event_types: type[Event]):
        """
        A decorator that registers a consumer for a given event type.
        Parameters:
            event_types: The event types to be registered.
        """
        def decorator(consumer: Callable[[Event], None]):   
            for event_type in event_types:
                self.add_event_handler(event_type, consumer)
            return consumer
        return decorator

    def register(self, command_type: type[Command]):
        """
        A decorator that registers a handler for a given command type.
        Parameters:
            command_type: The type of the command.
        """
        def decorator(handler: Callable[[Command], None]):
            self.add_command_handler(command_type, handler)
            return handler
        return decorator

    def add_command_handler(self, command_type: type[Command], handler: Callable[[Command], None]):
        """
        Sets a handler for a given command type. A command type can only have one handler.
        Parameters:
            command_type: The type of the command.
            handler: The handler to be registered.
        """
        self.command_handlers[command_type] = handler

    def add_event_handler(self, event_type: type[Event], consumer: Callable[[Event], None]):
        """
        Adds a consumer for a given event type. An event type can have multiple consumers.
        Parameters:
            event_type: The type of the event.
            consumer: The consumer to be added.
        """
        self.event_handlers.setdefault(event_type, []).append(consumer)

    def handle(self, message: Event | Command):
        """
        Handles a given message by invoking its corresponding handler or executing it by default.
        Parameters:
            message: The message to be handled.
        """
        
        if isinstance(message, Command):
            self.handle_command(message)
        elif isinstance(message, Event):
            self.handle_event(message)

    def handle_command(self, command: Command):
        """
        Handles a given command by invoking its corresponding handler 
        or executing it by default.

        Parameters:
            command: The command to be handled.
        """
        handler = self.command_handlers.get(type(command), None)
        command.execute() if not handler else handler(command)

    def handle_event(self, event: Event):
        """
        Handles a given event by invoking its registered consumers.

        Parameters:
            event: The event to be consumed.
        """
        for consumer in self.event_handlers.get(type(event), []):
            try:
                consumer(event)
            except Exception as exception:
                logger.error(f"Error {exception} while consuming event {event}")
                logger.debug(exception, exc_info=True)
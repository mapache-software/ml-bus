from abc import ABC, abstractmethod
from typing import Callable
from logging import getLogger
from collections import deque

logger = getLogger(__name__)

class Event(ABC):
    """
    Event is an abstract base class for domain events.
    """

class Command(ABC):
    """
    Command is a class representing a request to perform an action.
    """
    ...
    @abstractmethod
    def execute(self):
        """
        Executes the command.
        """
        ...

class Messagebus:
    """
    Messagebus is a class that routes domain events and commands to their respective handlers.

    Attributes:
        handlers: A dictionary mapping command types to their corresponding handlers.
        consumers: A dictionary mapping event types to a list of their consumers.
    """

    def __init__(self):
        self.handlers = dict[type[Command], Callable[[Command], None]]()
        self.consumers = dict[type[Event], list[Callable[[Event], None]]]()
        self.queue = deque[Command | Event]()

    def register(self, command_type: type[Command], handler: Callable[[Command], None]):
        """
        Sets a handler for a given command type. A command type can only have one handler.
        Parameters:
            command_type: The type of the command.
            handler: The handler to be registered.
        """
        self.handlers[command_type] = handler

    def subscribe(self, event_type: type[Event], consumer: Callable[[Event], None]):
        """
        Adds a consumer for a given event type. An event type can have multiple consumers.
        Parameters:
            event_type: The type of the event.
            consumer: The consumer to be added.
        """
        self.consumers.setdefault(event_type, []).append(consumer)

    def handle(self, command: Command):
        """
        Handles a given command by invoking its corresponding handler 
        or executing it by default.

        Parameters:
            command: The command to be handled.
        """
        handler = self.handlers.get(type(command), None)
        command.execute() if not handler else handler(command)

    def consume(self, event: Event):
        """
        Consumes a given event by invoking its registered consumers.

        Parameters:
            event: The event to be consumed.
        """
        for consumer in self.consumers.get(type(event), []):
            try:
                consumer(event)
            except Exception as exception:
                logger.error(f"Error while consuming event {event}")
                logger.debug(exception, exc_info=True)
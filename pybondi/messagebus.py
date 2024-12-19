from abc import ABC
from typing import Callable
from typing import Optional
from typing import Any
from logging import getLogger
from fast_depends import inject as _inject
from fast_depends import Provider as _Provider

logger = getLogger(__name__)

class Event(ABC):
    """
    An abstract base class for domain events.

    Events represent something that has occurred within the system. All domain events 
    should inherit from this class to ensure they are recognized by the message bus 
    and handled accordingly.
    """

class Command(ABC):
    """
    Commands represent a request to perform a specific action or operation within the system.
    All commands should inherit from this class to ensure they are recognized and processed 
    by the message bus.
    """
    def execute(self):
        """
        Executes the command.

        Subclasses may provide an implementation of this method, defining the specific 
        action to be performed when the command is executed. This implementation will be
        overridden if the messagebus have a command handler for the command.

        Raises:
            NotImplementedError: If the method is not overridden by the subclass.
        """
        raise NotImplementedError("Subclasses should implement the execute method.")


class Messagebus:
    """
    A class responsible for routing domain events and commands to their respective handlers.

    The `Messagebus` facilitates the decoupling of commands and events from their handling logic,
    promoting a clean and maintainable architecture.

    Parameters:
        `raise_on_event_error` (bool): 
            A flag indicating whether to raise an exception when an error occurs while consuming an event.
            Defaults to True.

    Attributes:
        `command_handlers` (dict[type[Command], Callable[[Command], None]]):
            A dictionary mapping command types to their corresponding handler functions.
        
        `event_handlers` (dict[type[Event], list[Callable[[Event], None]]]):
            A dictionary mapping event types to a list of handler functions.
    """

    def __init__(self, raise_on_event_error: Optional[bool] = True):
        self.raise_on_event_error = raise_on_event_error
        self.command_handlers = dict[type[Command], Callable[[Command], None]]()
        self.event_handlers = dict[type[Event], list[Callable[[Event], None]]]()
        self.dependency_provider = _Provider()

    @property
    def dependency_overrides(self) -> dict[Callable[..., Any], Callable[..., Any]]:
        return self.dependency_provider.dependency_overrides

    def handle(self, message: Event | Command):
        """
        Handles a given message by invoking its corresponding handler or executing it by default.

        Parameters:
            `message` (Event | Command): The message to be handled.
        """
        if isinstance(message, Command):
            self.handle_command(message)
        elif isinstance(message, Event):
            self.handle_event(message)

    def handle_command(self, command: Command):
        """
        Handles a given command by invoking its registered handler.

        If no handler is registered for the command type, the command's default `execute` method is called.

        Parameters:
            `command` (Command):
                The command to be handled.
        """
        handler = self.command_handlers.get(type(command), None)
        command.execute() if not handler else handler(command)

    def handle_event(self, event: Event):
        """
        Handles a given event by invoking all registered handlers for the event type.

        If an error occurs while consuming the event, the error is logged. Depending on the
        `raise_on_event_error` flag, the exception may be raised.

        Parameters:
            `event` (Event): The event to be consumed.
            
        Raises:
            Exception:
                If `raise_on_event_error` is `True` and an error occurs while consuming the event.
        """
        for handler in self.event_handlers.get(type(event), []):
            try:
                handler(event)
            except Exception as exception:
                logger.error(f"Error {exception} while consuming event {event}")
                logger.debug(exception, exc_info=True)
                if self.raise_on_event_error:
                    raise
               

    def add_command_handler(self, command_type: type[Command], handler: Callable[[Command], None]):
        """
        Registers  a handler for a given command type. A command type can only have one handler. 
        If a handler for the command type already exists, the new handler will replace the existing one.

        Parameters:
            `command_type`: The type of the command.
            `handler`: The handler to be registered. It should accept a single argument of the command type. 
        """
        handler_with_inject = _inject(dependency_overrides_provider=self.dependency_provider)(handler)
        self.command_handlers[command_type] = handler_with_inject


    def add_event_handler(self, event_type: type[Event], handler: Callable[[Event], None]):
        """
        Adds a handler for a given event type. An event type can have multiple handlers.
        Parameters:
            `event_type`: The type of the event.
            `handler`: The handler to be added. It should accept a single argument of the event type.
        """    
        handler_with_inject = _inject(dependency_overrides_provider=self.dependency_provider)(handler)
        self.event_handlers.setdefault(event_type, []).append(handler_with_inject)
                
                
    def on(self, *event_types: type[Event]):
        """
        A decorator that registers a handler for a given event type.
        Parameters:
            `event_types`: The event types to be registered.

        Example:

        messagebus = Messagebus()
        
        @messagebus.on(EventType)
        def handle_event(event: EventType, dependency: DependencyType = Depends(actual_dependency)):
            ...

        @messagebus.on(EventType2, EventType3)
        def handle_two_events(event: EventType1 | EventType2, dependency: DependencyType = Depends(abc_dependency)):
            ...
            
        messagebus.dependency_overrides[abc_dependency] = actual_dependency
        messagebus.handle(EventType("Something happened!"))
        """
        def decorator(handler: Callable[[Event], None]):
            handler_with_inject = _inject(dependency_overrides_provider=self.dependency_provider)(handler)
            for event_type in event_types:
                self.event_handlers.setdefault(event_type, []).append(handler_with_inject)
            return handler_with_inject
        return decorator

    def register(self, command_type: type[Command]):
        """
        A decorator that registers a handler for a given command type.
        Parameters:
            `command_type`: The type of the command.

        Example:

        @messagebus.register(CommandType)
        def handle_command(command: CommandType, dependency: DependencyType = Depends(some_dependency)):
            ...

        messagebus.handle(CommandType("Do something!"))
        """
        def decorator(handler: Callable[[Command], None]):
            handler_with_inject = _inject(dependency_overrides_provider=self.dependency_provider)(handler)
            self.command_handlers[command_type] = handler_with_inject
            return handler_with_inject
        return decorator
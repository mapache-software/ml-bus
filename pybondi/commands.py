from typing import Callable
from typing import Any
from inspect import signature

from fast_depends import inject
from fast_depends import Provider

class Command:
    """
    Represents a base class for commands. Commands are objects that encapsulate
    the data required to perform a specific action or operation.

    This class is intended to be subclassed to define concrete command types
    with the required attributes.
    """
    ...
    def execute(self):
        """
        Executes the command. This method may be overridden by subclasses to provide
        a default implementation for handling the command.
        """
        raise NotImplementedError(f"Not handler nor execute method found for command {self.__class__.__name__}")


class Commands:
    """
    Manages the registration and handling of commands and their associated handlers.

    Attributes:
        key_generator (Callable[[str], str]): A function used to generate keys for commands 
            based on their class names. Defaults to an identity function.
        types (dict[str, type[Command]]): A dictionary mapping command keys to their types.
        handlers (dict[str, Callable[[Command], None]]): A dictionary mapping command keys 
            to their respective handler functions.

    Methods:
        handle(command: Command) -> None:
            Handles a command by invoking its registered handler. Raises a KeyError if 
            no handler is found for the command's key.

        register(command_type: type[Command], handler: Callable[[Command], None]) -> None:
            Registers a command type and its corresponding handler function.

        handler(wrapped: Callable[[Command], Any]) -> Callable:
            Decorator for registering a handler function for one or more command types.

    Example:
        .. code-block:: python
        from dataclasses import dataclass
        from pybondi import Commands

        commands = Commands()
        db = {}  # Database

        @dataclass
        class CreateUser(Command):
            id: str
            name: str

        @dataclass
        class UpdateUser(Command):
            id: str
            name: str

        @commands.handler
        def put_user(command: CreateUser | UpdateUser):
            db[command.id] = command.name

        commands.handle(CreateUser(id='1',name='Alice'))
        commands.handle(UpdateUser(id='1',name='Bob'))
        print(db)  # Output: {'1': 'Bob'}
    """
        
    def __init__(self, key_generator: Callable[[str], str] = lambda name: name, provider: Provider = None, cast_dependency: bool = True):
        """
        Initializes the Commands instance.

        Args:
            key_generator (Callable[[str], str], optional): A function to generate command keys 
                from class names. Defaults to a lambda returning the class name unchanged.
            provider (Provider, optional): A provider instance to use for dependency injection.
            cast_dependency (bool, optional): Whether to cast the dependencies to the expected type.
        """
        self.cast_dependency = cast_dependency
        self.provider = provider or Provider()
        self.key_generator = key_generator
        self.types = dict[str, type[Command]]()
        self.handlers = dict[str, Callable[[Command], None]]()

    def handle(self, command: Command) -> None:
        """
        Handles a command by invoking its associated handler.

        Args:
            command (Command): The command to handle.

        Raises:
            KeyError: If no handler is found for the command's key.
        """
        key = self.key_generator(command.__class__.__name__)
        handler = self.handlers.get(key, None)
        handler(command) if handler else command.execute()
    
    def register(self, command_type: type[Command], handler: Callable[[Command], None]):
        """
        Registers a command type and its handler.

        Args:
            command_type (type[Command]): The type of the command to register.
            handler (Callable[[Command], None]): The handler function for the command.
        """
        key = self.key_generator(command_type.__name__)
        self.types[key] = command_type
        self.handlers[key] = inject(handler, dependency_overrides_provider=self.provider, cast=self.cast_dependency)

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
        function_signature = signature(wrapped)
        parameter = next(iter(function_signature.parameters.values()))
        if hasattr(parameter.annotation, '__args__'):
            for message_type in getattr(parameter.annotation, '__args__'):
                self.register(message_type, wrapped)
        else:
            message_type = parameter.annotation
            self.register(message_type, wrapped)
        return wrapped
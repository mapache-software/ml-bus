from collections import deque
from typing import Callable

from pybondi.aggregate import Aggregate
from pybondi.messagebus import Messagebus, Command, Event
from pybondi.repository import Repository
from pybondi.publisher import Publisher
from pybondi.publisher import Base as Subscriber

class Session:
    """
    A session manages a unit of work, cordinates the repository, the message bus and
    the publisher, mantaing the transactional boundaries.
    """
    subscribers = list[Subscriber]()
    event_handlers = dict[type[Event], list[Callable[[Event], None]]]()
    command_handlers = dict[type[Command], Callable[[Command], None]]()

    @classmethod
    def add_event_handler(cls, event_type: type[Event], handler: Callable[[Event], None]):
        """
        Adds an event handler for a given event type.
        """
        cls.event_handlers.setdefault(event_type, []).append(handler)

    @classmethod
    def add_command_handler(cls, command_type: type[Command], handler: Callable[[Command], None]):
        """
        Adds a command handler for a given command type.
        """
        cls.command_handlers[command_type] = handler

    @classmethod
    def subscribe(cls, subscriber: Subscriber):
        """
        Subscribes a subscriber to the session.
        """
        cls.subscribers.append(subscriber)

    def __init__(self, repository: Repository = None, publisher: Publisher = None, messagebus: Messagebus = None):
        self.repository = repository or Repository()
        self.queue = deque[Command | Event]()

        if publisher:
            self.publisher = publisher
        else:
            self.publisher = Publisher()
            for subscriber in self.subscribers:
                self.publisher.subscribe(subscriber)

        if messagebus:
            self.messagebus = messagebus
        else:
            self.messagebus = Messagebus()
            for event_type, handlers in self.event_handlers.items():
                [self.messagebus.subscribe(event_type, handler) for handler in handlers]
            for command_type, handler in self.command_handlers.items():
                self.messagebus.register(command_type, handler)

    def enqueue(self, message: Command | Event):
        """
        Enqueues a message in the session queue.
        """
        self.queue.append(message)

    def dequeue(self) -> Command | Event:
        """
        Dequeues a message from the session queue.
        """
        return self.queue.popleft()

    def add(self, aggregate: Aggregate):
        """
        Adds an aggregate to the repository.
        """
        self.repository.add(aggregate)

    def dispatch(self, message: Command | Event):
        """
        Dispatches a message to the message bus.
        """
        if isinstance(message, Command):
            self.messagebus.handle(message)
        elif isinstance(message, Event):
            self.messagebus.consume(message)

    def run(self):
        """
        Processes all messages in the queue.
        """
        while self.queue:
            message = self.dequeue()
            self.dispatch(message)
            
            for aggregate in self.repository.aggregates.values():
                while aggregate.root.events:
                    event = aggregate.root.events.popleft()
                    self.enqueue(event)


    def execute(self, command: Command):
        """
        Executes a command by enqueuing it in the message bus and processing all messages in the queue.
        """
        self.enqueue(command)
        self.run()

    def begin(self):
        """
        Begins a new transaction.
        """
        self.publisher.begin()

    def commit(self):
        """
        Commits changes from the transaction.
        """
        self.repository.commit(), self.publisher.commit()

    def rollback(self):
        """
        Rolls back changes of the transaction.
        """
        self.repository.rollback(), self.publisher.rollback()

    def close(self):
        """
        Closes the session. If the session queue is not empty, raises an exception.
        """
        self.repository.close(), self.publisher.close()
        if self.queue:
            raise Exception("Session queue is not empty")

    def __enter__(self):
        self.publisher.begin()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.run()
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()
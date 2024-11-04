from collections import deque
from typing import Callable
from logging import getLogger

from mlbus.aggregate import Event
from mlbus.aggregate import Aggregate
from mlbus.publisher import Publisher
from mlbus.messages import Command
from mlbus.repository import Repository

logger = getLogger(__name__)

class Bus:
    def __init__(self):
        self.handlers = dict[type[Command], Callable[[Command], None]]()
        self.consumers = dict[type[Event], list[Callable[[Event], None]]]()

    def handle(self, command: Command):
        handler = self.handlers.get(type(command), None)
        if not handler:
            raise ValueError(f"Command not found for message {command}")
        handler(command)

    def consume(self, event: Event):
        for consumer in self.consumers.get(type(event), []):
            try:
                consumer(event)
            except:
                logger.error(f"Error while consuming event {event}")

class Session:
    def __init__(self, repository: Repository | None = None, bus: Bus = None):
        self.bus = bus or Bus()
        self.queue = deque()
        self.repository = repository
    
    def bind(self, publisher: Publisher):
        self.publisher = publisher

    def add(self, aggregate: Aggregate):
        self.repository.add(aggregate)

    def execute(self, command: Command):
        self.queue.append(command)
        while self.queue:
            message = self.queue.popleft()
            if isinstance(message, Command):
                self.bus.handle(command)
            elif isinstance(message, Event):
                self.bus.consume(message)
            else:
                raise TypeError(f"The message {message} wasn't an event nor a command instance")
            for event in self.repository.collect():
                self.queue.append(event)
            
    def begin(self):
        self.publisher.begin()

    def commit(self):
        if self.repository:
            self.repository.commit()
        self.publisher.commit()

    def rollback(self):
        if self.repository:
            self.repository.rollback()
        self.publisher.rollback()

    def close(self):
        self.publisher.close()

    def __enter__(self):
        self.begin()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()    
from logging import getLogger
from mlbus.aggregate import Event
from mlbus.aggregate import Aggregate
from mlbus.publisher import Publisher
from mlbus.repository import Repository
from mlbus.messagebus import Command, Event, Messagebus

logger = getLogger(__name__)

class Session:
    def __init__(self, repository: Repository | None = None, bus: Messagebus = None):
        self.bus = bus or Messagebus()
        self.repository = repository
    
    def bind(self, publisher: Publisher):
        self.publisher = publisher

    def add(self, aggregate: Aggregate):
        self.repository.add(aggregate)

    def execute(self, command: Command):
        self.bus.enqueue(command)
        while self.bus.queue:
            message = self.bus.dequeue()
            if isinstance(message, Command):
                self.bus.handle(command)
            elif isinstance(message, Event):
                self.bus.consume(message)
            else:
                raise TypeError(f"The message {message} wasn't an event nor a command instance")
            for event in self.repository.collect():
                self.bus.enqueue(event)
            
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
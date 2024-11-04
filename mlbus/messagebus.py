from collections import deque
from typing import Callable
from logging import getLogger

logger = getLogger(__name__)

class Event: ...

class Command: ...

class Messagebus:
    def __init__(self):
        self.handlers = dict[type[Command], Callable[[Command], None]]()
        self.consumers = dict[type[Event], list[Callable[[Event], None]]]()
        self.queue = deque[Command | Event]()

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

    def enqueue(self, message: Event | Command):
        self.queue.append(message)

    def dequeue(self) -> Event | Command:
        return self.queue.popleft()
from typing import Any
from abc import ABC, abstractmethod

class Subscriber(ABC):

    @abstractmethod
    def receive(self, message: Any): ...

    @abstractmethod
    def begin(self): ...

    @abstractmethod
    def commit(self): ...

    @abstractmethod
    def rollback(self): ...
        
    @abstractmethod
    def close(self): ...


class Publisher:
    def __init__(self):
        self.subscribers = dict[str, list[Subscriber]]()

    def subscribe(self, topic: str, subscriber: Subscriber):
        self.subscribers.setdefault(topic, []).append(subscriber)

    def publish(self, topic: str, message: Any):
        for subscriber in self.subscribers.get(topic, []):
            subscriber.receive(message)

    def commit(self):
        for list in self.subscribers.values():
            [subscriber.commit() for subscriber in list]

    def rollback(self):
        for list in self.subscribers.values():
            [subscriber.rollback() for subscriber in list]

    def begin(self):
        for list in self.subscribers.values():
            [subscriber.begin() for subscriber in list]

    def close(self):
        for list in self.subscribers.values():
            [subscriber.close() for subscriber in list]
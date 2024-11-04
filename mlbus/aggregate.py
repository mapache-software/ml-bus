from abc import ABC, abstractmethod
from collections import deque
from mlbus.messagebus import Event

class Root:
    def __init__(self, hash: str):
        self.id = None
        self.hash = hash
        self.epochs = 0
        self.events = deque[Event]()
        
    def publish(self, event: Event):
        self.events.append(event)


class Aggregate(ABC):
    root: Root
    phase: str

    @property
    def epoch(self) -> int:
        return self.root.epochs
    
    @epoch.setter
    def epoch(self, value: int):
        self.root.epochs = value

    @abstractmethod
    def fit(self, *args, **kwargs): ...

    @abstractmethod
    def evaluate(self, *args, **kwargs): ...

class Compiler(ABC):

    def compile(self, *args, **kwargs) -> Aggregate: ...
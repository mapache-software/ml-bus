from typing import Optional
from typing import Any
from abc import ABC, abstractmethod
from collections import deque
from mlregistry import get_hash
from messages import Event

def identity(model: Any) -> Optional[str]:
    try:
        return get_hash(model)
    except:
        return None    

class Root:
    def __init__(self):
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
from abc import ABC, abstractmethod
from typing import Any
from typing import Sequence
from mlbarrel.messages import Metric
from mlbarrel.publisher import Publisher, Default
from enum import StrEnum

class Callback(ABC):
    def __init__(self):
        self.publisher = Publisher()
        self.publisher.subscribe('result', Default())
        self.phase = None
        self.epoch = None
        self.batch = None

    def bind(self, publisher: Publisher):
        self.publisher = publisher

    @abstractmethod
    def __call__(self, *args, **kwargs): ...

    @abstractmethod
    def flush(self): ...

    @abstractmethod
    def reset(self): ...
        

class Grouped(Callback):
    def __init__(self, callbacks: Sequence[Callback]):
        super().__init__()
        self.callbacks = list[Callback](callbacks)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ['phase', 'epoch', 'batch', 'publisher'] and hasattr(self, name):
            [setattr(callback, name, value) for callback in self.callbacks]
        return super().__setattr__(name, value)
    
    def bind(self, publisher: Publisher):
        [callback.bind(publisher) for callback in self.callbacks]

    def __call__(self, *args, **kwargs):
        [callback(*args, **kwargs) for callback in self.callbacks]

    def reset(self):
        [callback.reset() for callback in self.callbacks]

    def flush(self):
        [callback.flush() for callback in self.callbacks]
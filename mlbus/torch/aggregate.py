from abc import ABC
from typing import Protocol
from typing import Iterator
from typing import Any
from typing import overload

from torch import Tensor
from torch.nn import Module
from torch.optim import Optimizer

from mlbus.aggregate import Root
from mlbus.aggregate import Aggregate as Base

class Loader(Protocol):
    def __iter__(self) -> Iterator[Any]: ...

    @overload
    def __iter__(self) -> Iterator[tuple[Tensor, Tensor]]: ...

class Criterion(Protocol):
    def __call__(self, *args, **kwargs) -> Tensor: ...

class Aggregate(Module, Base):
    def __init__(self, identifier: str):
        super().__init__()
        self.root = Root(identifier)

    @property
    def phase(self) -> str:
        return 'train' if self.training else 'evaluation'
    
    @phase.setter
    def phase(self, value: str):
        self.train() if value == 'train' else self.eval()
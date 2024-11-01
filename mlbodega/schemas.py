from uuid import UUID
from typing import Any
from dataclasses import dataclass, asdict, field

class Schema:
    def dict(self):
        return asdict(self)

@dataclass
class Experiment(Schema):
    id: UUID
    name: str

@dataclass
class Module(Schema):
    id: UUID
    type: str
    hash: str
    name: str
    args: list[Any]
    kwargs: dict[str, Any]

@dataclass
class Model(Module):
    type: str = field(default='model', init=False)
    epoch: int

@dataclass
class Metric(Schema):
    name: str
    value: float
    batch: int
    epoch: int
    phase: str

@dataclass
class Session(Schema):
    hash: str
    phase: str
    kwargs: dict[str, Any]
    epochs: tuple[int, int]
    dataset: Module
    modules: list[Module]
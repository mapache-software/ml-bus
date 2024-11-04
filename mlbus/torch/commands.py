from dataclasses import dataclass
from typing import Sequence
from mlbus.aggregate import Aggregate
from mlbus.callbacks import Callback
from mlbus.torch.loaders import Loader

class Command:...

@dataclass
class Train(Command):
    aggregate: Aggregate
    loader: Loader
    callback: Callback
    count_epoch: bool = True

@dataclass
class Evaluate(Command):
    aggregate: Aggregate
    loader: Loader
    callback: Callback
    count_epoch: bool = True

@dataclass
class Iterate(Command):
    aggregate: Aggregate
    loaders: Sequence[tuple[str, Loader]]
    callback: Callback
    count_epoch: bool = True
    
@dataclass
class Store(Command):
    aggregate: Aggregate

@dataclass
class Restore(Command):
    aggregate: Aggregate
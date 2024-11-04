from abc import ABC, abstractmethod
from typing import Generator
from mlbus.messages import Event
from mlbus.aggregate import Aggregate

class Repository:
    def __init__(self):
        self.aggregates = dict[str, Aggregate]()

    def add(self, aggregate: Aggregate):
        self.aggregates[aggregate.root.hash] = aggregate

    def collect(self) -> Generator[Event, None, None]:
        for aggregate in self.aggregates.values():
            while aggregate.root.events:
                yield aggregate.root.events.popleft()

    def commit(self):
        for aggregate in self.aggregates.values():
            self.store(aggregate)

    def rollback(self):
        for aggregate in self.aggregates.values():
            self.restore(aggregate)

    @abstractmethod
    def store(self, aggregate: Aggregate): ...

    @abstractmethod
    def restore(self, aggregate: Aggregate): ...
from abc import ABC, abstractmethod
from mlbodega.schemas import Experiment, Model, Metric, Session

class Experiments:

    @abstractmethod
    def add(self, experiment: Experiment): ...

    @abstractmethod
    def get(self, name: str): ...

    @abstractmethod
    def list(self) -> list[Experiment]: ...

    @abstractmethod
    def remove(self, experiment: Experiment): ...

    @abstractmethod
    def update(self, experiment: Experiment): ...


class Metrics:
    @abstractmethod
    def add(self, metric: Metric, model: Model): ...   

    @abstractmethod
    def list(self, model: Model) -> list[Metric]: ...


class Sessions:
    @abstractmethod
    def put(self, session: Session, model: Model): ...

    @abstractmethod
    def list(self, model: Model) -> list[Session]: ...
    

class Models:
    experiment: Experiment
    metrics: Metrics

    @abstractmethod
    def add(self, model: Model): ...

    @abstractmethod
    def get(self, hash: str): ...

    @abstractmethod
    def list(self) -> list[Model]: ...

    @abstractmethod
    def remove(self, model: Model): ...

    @abstractmethod
    def update(self, model: Model): ...
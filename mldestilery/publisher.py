from typing import Any
from abc import ABC, abstractmethod
from mldestilery.messages import Metric
from logging import getLogger

logger = getLogger(__name__)

class Subscriber(ABC):

    @abstractmethod
    def receive(self, message: Any): ...

class Default(Subscriber):

    def receive(self, message: Metric):
        assert isinstance(message, Metric)
        logger.info(f'On phase {message.phase} Epoch {message.epoch} Batch {message.batch} {message.name} {message.value}')

class Publisher:
    def __init__(self):
        self.subscribers = dict[str, list[Subscriber]]()

    def subscribe(self, topic: str, subscriber: Subscriber):
        self.subscribers.setdefault(topic, []).append(subscriber)

    def publish(self, topic: str, message: Any):
        for subscriber in self.subscribers.get(topic, []):
            subscriber.receive(message)
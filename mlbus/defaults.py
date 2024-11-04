from typing import Any
from abc import ABC, abstractmethod
from logging import getLogger
from dataclasses import dataclass
from mlbus.messagebus import Message
from mlbus.publisher import Subscriber as Base

logger = getLogger(__name__)

@dataclass
class Metric(Message):
    name: str
    value: float
    batch: int
    epoch: int
    phase: str

class Subscriber(Base):

    def receive(self, message: Metric):
        assert isinstance(message, Metric)
        logger.info(f'On phase {message.phase} Epoch {message.epoch} Batch {message.batch} {message.name} {message.value}')
    
    def commit(self):
        logger.info('Committing publisher')

    def begin(self):
        logger.info('Starting publisher')

    def rollback(self):
        logger.info('Rolling back the publisher')

    def close(self):
        logger.info('Closing the publisher')

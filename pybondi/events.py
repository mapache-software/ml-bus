from abc import ABC
from dataclasses import dataclass
from pybondi.aggregate import Aggregate

class Event(ABC):
    """
    An abstract base class for domain events. All events should inherit from this class, otherwise
    they will not be recognized by the message bus.
    """

@dataclass
class Added[T: Aggregate](Event):
    '''
    The Added[Aggregate] event is used to signal that the aggregate has been added to a session.
    '''
    aggregate: T

@dataclass
class RolledBack[T: Aggregate](Event):
    '''
    The RolledBack[Aggregate] event is used to signal that the aggregate has been rolled back in the session.
    '''
    aggregate: T

@dataclass
class Saved[T: Aggregate](Event):
    '''
    The Saved[Aggregate] event is used to signal that the aggregate has been committed in the session.
    '''
    aggregate: T
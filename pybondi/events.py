from abc import ABC
from dataclasses import dataclass
from pybondi.aggregate import Aggregate

class Event(ABC):
    """
    Event is an abstract base class for domain events.
    """

@dataclass
class Added[T: Aggregate](Event):
    '''
    The Added[Aggregate] event is used to signal that the aggregate has been added to a session.
    '''
    aggregate: T
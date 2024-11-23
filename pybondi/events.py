from dataclasses import dataclass
from pybondi.aggregate import Aggregate
from pybondi.messagebus import Event

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
class Commited[T: Aggregate](Event):
    '''
    The Saved[Aggregate] event is used to signal that the aggregate has been committed in the session.
    '''
    aggregate: T
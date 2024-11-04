from abc import ABC, abstractmethod
from typing import Any
from collections import deque
from mlbus.messagebus import Event

class Root:
    '''
    Root is a class that represents the root of an aggregate. It is responsible for
    mantaning the consistency of the aggregate by storing the events that have occurred

    Attributes:
        id: The unique identifier of the aggregate.
        events: A deque storing the events that have occurred on the aggregate.
    '''

    def __init__(self, id: Any):
        self.id = id
        self.events = deque[Event]()

    def publish(self, event: Event):
        '''
        Publishes an event to the aggregate.
        Parameters:
            event: The event to be published.
        '''
        self.events.append(event)


class Aggregate(ABC):
    '''
    Aggregate is an abstract class that represents a collection of domain objects that are
    treated as a single unit. It is responsible for maintaining the consistency of the
    domain objects by applying events to them.

    Attributes:
        root: The root of the aggregate.
    '''
    
    root: Root

    def __init__(self, root: Root):
        self.root = root
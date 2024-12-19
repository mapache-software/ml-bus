from abc import ABC
from typing import Any
from collections import deque
from pybondi.messagebus import Event
from abc import ABC, abstractmethod

class Entity(ABC):
    """
    Represents a base entity with a unique identifier. Entities are equal if their IDs are equal.
    ID is a read-only attribute and cannot be modified once set.

    Attributes:
        id (Any): The unique identifier of the entity.
    """
    def __init__(self, id: Any):
        self.id = id

    def __eq__(self, other: object) -> bool:
        '''
        Compares two entities based on their ID.
        '''

        if not isinstance(other, Entity):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        '''
        Returns the hash of the entity ID.
        '''
        return hash(self.id)
    
    def __setattr__(self, name, value):
        '''
        Prevents modification of the entity ID.
        '''
        if name == 'id' and hasattr(self, 'id'):
            raise AttributeError('Cannot modify the entity ID.')
        super().__setattr__(name, value)


class Root(Entity):
    """
    Represents the root entity of an aggregate, responsible for publishing events and
    maintaining consistency within the aggregate.
    """

    def __init__(self, id: Any):
        super().__init__(id)
        self.events = deque[Event]()
    
    def publish(self, event: Event):
        """
        Adds an event to the root entity's event queue. The
        event will be collected and processed in a session.

        Args:
            event (Event): The event to be added to the event queue.
        """
        self.events.append(event)


class Aggregate(ABC):
    """
    Abstract base class for aggregates that contain a root entity.

    Attributes:

        root (Root): The root entity of the aggregate.
    """
    root: Root


class Factory[T: Aggregate](ABC):

    @abstractmethod
    def __call__(self, *args, **kwds) -> T:
        '''
        Creates a new aggregate instance.
        '''
        ...
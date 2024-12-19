from abc import ABC
from pybondi.aggregate import Aggregate

class Repository[T: Aggregate](ABC):
    """
    Repository is an abstract class that defines the interface for storing and restoring aggregates.

    It maintains an internal identity map of aggregates and provides methods for:
    - Adding new aggregates to the map.
    - Committing changes to the underlying storage.
    - Rolling back changes to the previous state.

    Concrete subclasses must implement the `store` and `restore` methods to provide
    specific persistence and retrieval mechanisms for aggregates.
    """
    def __init__(self):
        self.aggregates = dict[str, Aggregate]()

    def add(self, aggregate: T):
        """
        Adds an aggregate to the internal identity map.

        Parameters:
            aggregate: The aggregate to be added.
        """
        self.aggregates[aggregate.root.id] = aggregate

    def commit(self):
        """
        Commits changes to the underlying storage for all stored aggregates.

        Iterates over each aggregate in the identity map and calls the `store` method
        to persist its current state.
        """
        for aggregate in self.aggregates.values():
            self.store(aggregate)

    def rollback(self):
        """
        Rolls back changes to the previous state for all stored aggregates.

        Iterates over each aggregate in the identity map and calls the `restore` method
        to load its previous state from storage.
        """
        for aggregate in self.aggregates.values():
            self.restore(aggregate)

    def begin(self):
        """
        Begins a new transaction for the repository.
        """
        pass

    def close(self):
        """
        Closes the repository and releases any resources.
        """
        self.aggregates.clear()

    def store(self, aggregate: T):
        """
        Stores the given aggregate to the underlying storage. Override this
        method with the specific storage mechanism.

        Args:
            aggregate: The aggregate to be stored.
        """
        pass


    def restore(self, aggregate: T):
        """
        Restores the given aggregate from the underlying storage . Override this
        method with the specific storage mechanism.

        Args:
            aggregate: The aggregate to be restored.
        """
        pass
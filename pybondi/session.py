from collections import deque
from pybondi.aggregate import Aggregate
from pybondi.messagebus import Messagebus, Command, Event
from pybondi.repository import Repository
from pybondi.publisher import Publisher
from pybondi.events import Added, RolledBack, Commited

class Session:
    """
    A session manages a unit of work, cordinates the repository, the message bus and
    the publisher, mantaing the transactional boundaries.
    """
    def __init__(self, messagebus: Messagebus = None,  publisher: Publisher = None, repository: Repository = None):
        self.repository = repository or Repository()
        self.messagebus = messagebus or Messagebus()
        self.publisher = publisher or Publisher()
        self.queue = deque()

    def enqueue(self, message: Command | Event):
        """
        Enqueues a message in the session queue.
        """
        self.queue.append(message)

    def dequeue(self) -> Command | Event:
        """
        Dequeues a message from the session queue.
        """
        return self.queue.popleft()

    def add(self, aggregate: Aggregate):
        """
        Adds an aggregate to the repository. Enqueues an Added event for the aggregate.
        In case that the aggregate state depends on external resources, the aggregate should
        bring it's state up to date using a handler for the Added event.
        """
        self.repository.add(aggregate)
        self.enqueue(Added(aggregate))

    def dispatch(self, message: Command | Event):
        """
        Dispatches a message to the message bus.
        """
        self.messagebus.handle(message)

    def run(self):
        """
        Processes all messages in the queue.
        """
        while self.queue:
            message = self.dequeue()
            self.messagebus.handle(message)
            
            for aggregate in self.repository.aggregates.values():
                while aggregate.root.events:
                    event = aggregate.root.events.popleft()
                    self.enqueue(event)


    def execute(self, command: Command):
        """
        Executes a command by enqueuing it in the message bus and processing all messages in the queue.
        """
        self.enqueue(command)
        self.run()

    def begin(self):
        """
        Begins a new transaction.
        """
        self.publisher.begin()

    def commit(self):
        """
        Commits changes from the transaction. Dispatches a Saved event for each aggregate
        for which changes were committed. In case that the aggregate state depends on external
        resources, it should be updated using a handler for the Saved event.
        """
        self.run()
        for aggregate in self.repository.aggregates.values():
            self.messagebus.handle(Commited(aggregate))
        self.repository.commit(), self.publisher.commit()

    def rollback(self):
        """
        Rolls back changes of the transaction. Dispatches a RolledBack event for each aggregate
        for which changes were rolled back. In case that the aggregate state depends on external
        resources, it should be restored to its previous state using a handler for the RolledBack event.
        """
        for aggregate in self.repository.aggregates.values():
            self.messagebus.handle(RolledBack(aggregate))
        self.queue.clear()
        self.repository.rollback(), self.publisher.rollback()

    def close(self):
        """
        Closes the session. If the session queue is not empty, raises an exception.
        """
        self.repository.close(), self.publisher.close()
        if self.queue:
            raise Exception("Session queue is not empty")

    def __enter__(self):
        self.publisher.begin()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.run()
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()
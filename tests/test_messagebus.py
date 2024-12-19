from logging import getLogger
from pybondi import Depends
from pybondi import Event, Command
from pybondi import Messagebus

logger = getLogger(__name__)

class MakeSomethingHappen(Command):
    def __init__(self, message: str):
        self.message = message

class SomethingHappened(Event):
    def __init__(self, message: str):
        self.message = message

class AnotherThingHappened(Event):
    def __init__(self, message: str):
        self.message = message

class ABCRepositoryDependency:
    data: list[str]

messagebus = Messagebus()

def get_repository_deps() -> ABCRepositoryDependency:
    raise NotImplementedError("Subclasses must implement the execute method.")

@messagebus.on(SomethingHappened, AnotherThingHappened)
def handle_something(event: SomethingHappened | AnotherThingHappened, repository: ABCRepositoryDependency = Depends(get_repository_deps)):
    repository.data.append(event.message)

@messagebus.on(AnotherThingHappened)
def handle_more(event: AnotherThingHappened, repository: ABCRepositoryDependency = Depends(get_repository_deps)):
    repository.data.append(event.message)

@messagebus.register(MakeSomethingHappen)
def handle_make_something(command: MakeSomethingHappen, repository: ABCRepositoryDependency = Depends(get_repository_deps)):
    repository.data.append(command.message)

class RepositoryDependency(ABCRepositoryDependency):
    def __init__(self):
        self.data = list()

repository = RepositoryDependency()

def actual_repository():
    return repository

messagebus.dependency_overrides[get_repository_deps] = actual_repository

def test_messagebus():
    messagebus.handle(MakeSomethingHappen("Hello"))
    messagebus.handle(SomethingHappened("World"))
    messagebus.handle(AnotherThingHappened("!"))
    assert repository.data == ["Hello", "World", "!", "!"]
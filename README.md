# py-bondi
A library for creating event driven systems using domain driven design.

### Installation

```bash
pip install pybondi
```

### Introduction

This library provides a framework for modeling complex domains using an event driven architecture and the pub/sub pattern. It provides:

- An in memory message bus for handling events and commands.
- A simple in memory publisher for publishing messages to external systems.
- A base aggregate root that can collect domain events and a base aggregate class.
- A base repository class for storing and retrieving aggregates.
- A session class for managing transactions and unit of work. 
- Default events for handling aggregate's state when it is added to a session, saved, or rolled back.

## Write domain logic using commands and events

You can define commands and events as classes that inherit from the Command and Event classes. A command is a request to do something, and an event is a notification that something has happened. 

You can handle commands and events by defining "handlers" that are functions that take a command or event as an argument. You can pass dependencies to handlers using dependency injection just like in FastAPI.

```python

from pybondi.messagebus import Event, Command
from pybondi.messagebus import Messagebus, Depends

class MakeSomethingHappen(Command):
    def __init__(self, message: str):
        self.message = message

class SomethingHappened(Event):
    def __init__(self, message: str):
        self.message = message

class AnotherThingHappened(Event):
    def __init__(self, message: str):
        self.message = message

class ABCRepositoryDependency: ### This simulates to be a repository dependency that we want to inject into our handlers.
    ### This can be a real database client, file system client, or any other service that we want to inject.
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
                         
messagebus.dependency_overrides[get_repository_deps] = actual_repository    ### We override the dependency with our mock API.
                                                                            ### Just like in FastAPI. This is not necessary but
                                                                            ### super useful.
messagebus.handle(MakeSomethingHappen("Hello"))
messagebus.handle(SomethingHappened("World"))
messagebus.handle(AnotherThingHappened("!"))
print(repository.data) # ["Hello", "World", "!", "!"]
```


## Publish messages to external systems (Pubsub)

You can publish messages to external systems adding handlers to a publisher class. This is an in memory implementation of the pub/sub pattern,
but you can easily replace it with a real pub/sub system like Redis or RabbitMQ.

```python

from pybondi.publisher import Message, Publisher, Depends

class ExternalAPI: ### This is a mock class for an external API that we want to publish messages to.
    ### This can be a real API client, or any other external system that we want to inject.
    def __init__(self):
        self.data = []

def abc_dependency() -> ExternalAPI: ...

publisher = Publisher()

@publisher.subscribe("topic-1")
def subscriber1(message: Message, api: ExternalAPI = Depends(abc_dependency)):
    api.data.append(message.payload)

@publisher.subscribe("topic-1", "topic-2")
def subscriber2(message: Message, api: ExternalAPI = Depends(abc_dependency)):
    api.data.append(message.payload)

api = ExternalAPI()
publisher.dependency_overrides[abc_dependency] = lambda: api ### We override the dependency with our mock API.
                                                             ### Just like in FastAPI. This is not necessary but
                                                             ### super useful.
                                                            

def test_publisher():
    publisher.publish("topic-1", Message("Hi"))
    publisher.rollback()
    publisher.publish("topic-2", Message("Hello"))
    publisher.publish("topic-2", Message("World"))
    publisher.publish("topic-1", Message("!"))
    publisher.commit()

    print(api.data) ### ["Hello", "World", "!", "!"]
```



## Define aggregates and repositories

You can define aggregates as classes that inherit from the Aggregate class. An aggregate is a collection of domain objects that are treated as a single unit. Each aggregate should have a root entity that is responsible for maintaining the consistency of the aggregate using events.

You can also define repositories as classes that inherit from the Repository class. A repository is an object that mediates between the domain objects and the database or other data store.

```python
from pybondi.aggregate import Aggregate, Root
from pybondi.repository import Repository

class User(Aggregate):
    def __init__(self, id: int, name: str):
        self.root = Root(id)
        self.name = name

    def change_name(self, name: str):
        self.root.publish(UsernameChanged(name))


class Users(Repository):
    def __init__(self):
        super().__init__()

    def store(self, user: User):
        database.save(user) ### Persists the user to the database.

    def restore(self, user: User):
        return database.load(user) ### Loads the user from the database to it's original state.
```

## Manage transactions and unit of work

Finally, you can wrap your domain logic in a session object that manages transactions and unit of work. A session is an object that represents a single transaction and will coordinate the messagebus, publisher, and repositories so if something goes wrong in some event, all changes can be rolled back.

```python


from pybondi import Command
from pybondi.session import Session


@messagebus.on(Added, RolledBack)
def bring_user_up_to_date(event: Added[User] | RolledBack[User]):
    event.user.age = fetch_user_age(event.user) ### Fetch the user's age from somewhere
    event.user.root.publish(AgeChanged(event.user.age)) ### You can publish events from events handlers
                                                        ### This way you can create a chain of events that
                                                        ### Will be executed in order.

@messagebus.on(Commited)
def save_user(event: Commited[User]):
    save_user_age(event.user) ### Send the user's age to somewhere this is just an example.
    
    
@dataclass
class BumpAge(Command):
    user: User

    def execute(self):
        self.user.age += 1 

with Session(messagebus, repository, publisher) as session:
    session.add(user)
    session.execute(BumpAge(user))

### user is now 1 year older

with Session(messagebus) as session:
    session.add(user)
    session.execute(BumpAge(user))
    raise Exception("Something went wrong")

### user don't get older because the session was rolled back
```


### License

This project is licensed under the terms of the MIT license.
```

# Welcome to the PyBondi library

This is the documentation for **PyBondi**. You will find all the information you need to get started, including guides, reference material, and examples.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Usage](#usage)
4. [License](#license)

## Introduction

PyBondi is a lightweight Python library that provides simple and intuitive tools for creating event driven systems with a FastAPI-like syntax thanks to the [fast-depends](https://github.com/Lancetnik/FastDepends) dependency injection system. It provides base classes and abstractions for the following patterns:

- **Event and Consumers**: Create and dispatch events to several consumers.
- **Commands and Handlers**: Create and dispatch commands to their respective handlers.
- **Messages and Publishers**: Create and publish messages to several publishers.
- **Services and Providers**: Create and use services and inject dependencies.
- **Sessions and the unit of work pattern**: Create and manage the lifecycle of resources using the unit of work pattern.

## Installation

Install with pip:

```bash
pip install pybondi
```

## Usage

Import the library and start defining your commands, events, messages, etc.

``` py
from pybondi import Command
from pybondi import Event
from pybondi import Message
from dataclasses import dataclass

### Define your commands, events, messages, etc.


@dataclass
class CreateUser(Command):
    id: str
    name: str

@dataclass
class UpdateUser(Command):
    id: str
    name: str

@dataclass
class UserUpdated(Event):
    id: str
    name: str

@dataclass
class Notification(Message):
    user_id: str
    text: str
```

Create a service and start defining your handlers, subscribers, consumers, etc. if you don't want to resolve your dependencies yet, you can use
dependency injection with `Depends` like in FastAPI.

For messages, one can define several topics in which the message will be published.

For commands and events the type hints will pair the command or event with the handler or consumer that will process it. You can use unions to pair several commands or events with the same handler or consumer.

``` py
from pybondi import Service
from pybondi import Depends


service = Service(cast_dependency=False) # Disable automatic casting for this example
                                         # this is needed because we are using dicts as dependencies
                                         # and they get empty when casting

def database_dependency() -> dict:
    raise NotImplementedError

def notifications_dependency() -> dict:
    raise NotImplementedError

@service.handler
def handle_put_user(command: CreateUser | UpdateUser, database = Depends(database_dependency)):
    database[command.id] = command.name
    service.consume(UserUpdated(id=command.id, name=command.name))

@service.consumer
def consume_user_updated(event: UserUpdated, database = Depends(database_dependency)):
    service.publish('topic-1', Notification(user_id=event.id, text=f'User {event.id} updated with name {event.name}')) 

@service.subscriber('topic-1', 'topic-2')
def on_notifications(message: Notification, notifications = Depends(notifications_dependency)):
    notifications[message.user_id] = message.text
```

Override the dependencies with implementations if you already didn't do it already.

``` py
nfs = {}
db = {}

def database_adapter():
    return db

def notification_adapter():
    return nfs

service.dependency_overrides[database_dependency] = database_adapter
service.dependency_overrides[notifications_dependency] = notification_adapter
```

Finally, execute your logic.

``` py
service.handle(CreateUser(id='1', name='John Doe'))
service.handle(UpdateUser(id='1', name='Jane Doe'))

print(db['1']) # Jane Doe
assert db['1'] == 'Jane Doe'

print(nfs['1']) # User 1 updated with name Jane Doe
assert nfs['1'] == 'User 1 updated with name Jane Doe'

```
You can see this example in the [examples](https://github.com/mr-mapache/py-bondi) folder. 

## License

This project is licensed under the terms of the MIT license. Feel free to use it in your projects.
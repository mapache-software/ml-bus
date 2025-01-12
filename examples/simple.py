from pybondi import Command
from pybondi import Event
from pybondi import Message
from dataclasses import dataclass

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
    

nfs = {}
db = {}

def database_adapter():
    return db

def notification_adapter():
    return nfs

service.dependency_overrides[database_dependency] = database_adapter
service.dependency_overrides[notifications_dependency] = notification_adapter

service.handle(CreateUser(id='1', name='John Doe'))
service.handle(UpdateUser(id='1', name='Jane Doe'))

print(db['1']) # Jane Doe
assert db['1'] == 'Jane Doe'

print(nfs['1']) # User 1 updated with name Jane Doe
assert nfs['1'] == 'User 1 updated with name Jane Doe'
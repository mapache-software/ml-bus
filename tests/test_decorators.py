from dataclasses import dataclass

from pybondi.commands import Commands
from pybondi.events import Events

commands = Commands()
events = Events()

@dataclass
class CreateUser:
    id: str
    name: str

@dataclass
class UpdateUser:
    id: str
    name: str

@dataclass
class UserUpdated:
    id: str

db = {} # Database
nfs = [] # Notification flags

@commands.handler
def put_user(command: CreateUser | UpdateUser):
    db[command.id] = command.name

@events.consumer
def on_user_updated(event: UserUpdated):
    db[event.id] = db[event.id] + ' updated'

@events.consumer
def on_user_updated_nf(event: UserUpdated):
    nfs.append(event.id)

def test_decorators():
    commands.handle(CreateUser('1', 'Alice'))
    commands.handle(UpdateUser('1', 'Bob'))
    events.consume(UserUpdated('1'))
    assert db['1'] == 'Bob updated'
    assert nfs == ['1']
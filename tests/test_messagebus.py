from typing import Any
from pytest import raises
from pytest import fixture
from pybondi import Event, Command
from pybondi import Messagebus
from pybondi import Aggregate, Root, Factory, Repository
from dataclasses import dataclass

class Entity(Aggregate):
    def __init__(self):
        super().__init__(root=Root(id=None))
        self.mutated = False

    def set_id(self, id):
        self.root.id = id
        self.root.publish(IDSetted(entity=self))

@dataclass
class IDSetted(Event):
    entity: Entity

    def dump(self) -> dict[str, Any]:
        return {'id': self.entity.root.id}

@dataclass
class CascadeEvent(Event):
    entity: Entity

@dataclass
class SetID(Command):
    entity: Entity
    def execute(self):
        self.entity.root.id = 1
        self.entity.root.publish(IDSetted(entity=self.entity))

something = {}
database = {}

def on_id_setted(event: IDSetted):
    event.entity.mutated = True
    event.entity.root.publish(CascadeEvent(entity=event.entity))

def on_cascade_event(event: CascadeEvent):
    something['event'] = 'cascade'

@fixture
def messagebus():
    mb = Messagebus()
    mb.subscribe(IDSetted, lambda event: database.update(event.dump()))
    mb.subscribe(IDSetted, on_id_setted)
    mb.subscribe(CascadeEvent, on_cascade_event)
    return mb

def test_messagebus_subscribe(messagebus: Messagebus):
    entity = Entity()
    command = SetID(entity=entity)
    messagebus.enqueue(command)
    while messagebus.queue:
        msg = messagebus.dequeue()
        if isinstance(msg, Command):
            msg.execute()
        elif isinstance(msg, Event):
            messagebus.consume(msg)
        while entity.root.events:
            event = entity.root.events.popleft()
            messagebus.enqueue(event)
            
    assert database == {'id': 1}
    assert entity.mutated == True
    assert something == {'event': 'cascade'}
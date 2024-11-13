from typing import Any
from pytest import fixture
from pybondi import Event, Command
from pybondi import Aggregate, Root
from pybondi import Session
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
def session():
    Session.event_handlers[IDSetted] = [on_id_setted, lambda event: database.update(event.dump())]
    Session.event_handlers[CascadeEvent] = [on_cascade_event]

def test_session(session):
    entity = Entity()
    with Session() as session:
        session.add(entity)
        session.execute(SetID(entity=entity))

    print(entity.mutated)
    assert entity.mutated
    assert database == {'id': 1}
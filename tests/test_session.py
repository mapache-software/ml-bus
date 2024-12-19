from pybondi.aggregate import Root
from pybondi.session import Session
from pybondi.events import Added, RolledBack, Commited
from pybondi.messagebus import Messagebus, Depends, Command
from dataclasses import dataclass

messagebus = Messagebus()
age = {'1': 18}

@dataclass
class User:
    age: int
    root: Root = Root('1')

@messagebus.on(Added, RolledBack)
def bring_user_up_to_date(event: Added[User] | RolledBack[User]):
    event.aggregate.age = age['1']

@messagebus.on(Commited)
def save_user(event: Commited[User]):
    age['1'] = event.aggregate.age

@dataclass
class BumpAge(Command):
    user: User

    def execute(self):
        self.user.age += 1 

def test_session():
    user = User(0)
    with Session(messagebus) as session:
        session.add(user)
        session.execute(BumpAge(user))

    assert age['1'] == 19
    assert user.age == 19
    
    with Session(messagebus) as session:
        session.add(user)
        session.execute(BumpAge(user))
        session.rollback()

    assert age['1'] == 19
    assert user.age == 19

    
from pytest import fixture, fail
from pybondi.publisher import Message, Publisher, Depends

class DAO:
    def __init__(self):
        self.data = []

def abc_dependency() -> DAO: ...

publisher = Publisher()

@publisher.subscribe("topic-1")
def subscriber1(message: Message, dao: DAO = Depends(abc_dependency)):
    dao.data.append(message.payload)

@publisher.subscribe("topic-1", "topic-2")
def subscriber2(message: Message, dao: DAO = Depends(abc_dependency)):
    dao.data.append(message.payload)

dao = DAO()
publisher.dependency_overrides[abc_dependency] = lambda: dao

def test_publisher():
    publisher.publish("topic-1", Message("Hi"))
    publisher.rollback()
    publisher.publish("topic-2", Message("Hello"))
    publisher.publish("topic-2", Message("World"))
    publisher.publish("topic-1", Message("!"))
    publisher.commit()

    assert dao.data == ["Hello", "World", "!", "!"]
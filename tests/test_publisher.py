from pytest import fixture
from pybondi.publisher import Publisher, Subscriber

def handle_event(event):
    assert event == 'data'

@fixture
def subscriber():
    subscriber = Subscriber()
    subscriber.subscribe('event', handle_event)
    return subscriber

@fixture
def publisher(subscriber):
    publisher = Publisher()
    publisher.subscribe(subscriber)
    return publisher

def test_publisher(publisher: Publisher):
    publisher.publish('event', 'data')
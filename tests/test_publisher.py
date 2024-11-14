from pytest import fixture, fail
from unittest.mock import Mock
from pybondi.publisher import Publisher

@fixture
def publisher():
    return Publisher()

def test_subscribe_and_publish_message(publisher: Publisher):
    subscriber = Mock()
    publisher.subscribe("topic1", subscriber)
    
    publisher.handle("topic1", "test message")
    publisher.commit()
    subscriber.assert_called_once_with("test message")

def test_multiple_subscribers_on_same_topic(publisher: Publisher):
    subscriber1 = Mock()
    subscriber2 = Mock()
    publisher.subscribe("topic1", subscriber1)
    publisher.subscribe("topic1", subscriber2)
    publisher.handle("topic1", "test message")
    publisher.commit()
    
    subscriber1.assert_called_once_with("test message")
    subscriber2.assert_called_once_with("test message")

def test_no_subscribers_no_errors(publisher: Publisher):
    # Handle a message with no subscribers
    publisher.handle("topic1", "test message")
    try:
        publisher.commit()
    except Exception as e:
        fail(f"Commit failed with error: {e}")

def test_rollback_message(publisher: Publisher):
    subscriber = Mock()
    publisher.subscribe("topic1", subscriber)
    
    publisher.handle("topic1", "test message")
    publisher.rollback()
    
    publisher.commit()
    subscriber.assert_not_called()

def test_begin_transaction(publisher: Publisher):
    subscriber = Mock()
    publisher.subscribe("begin", subscriber)
    
    publisher.begin()
    subscriber.assert_called_once_with(None)

def test_close_transaction(publisher: Publisher):
    subscriber = Mock()
    publisher.subscribe("close", subscriber)
    
    publisher.close()
    
    subscriber.assert_called_once_with(None)

from unittest.mock import MagicMock
from pybondi.publisher import Publisher
from pybondi.callbacks import Callback, Callbacks

class MockCallback(Callback):
    def __init__(self):
        super().__init__()
        self.called = False
        self.flushed = False
        self.reset_called = False

    def __call__(self, *args, **kwargs):
        self.called = True

    def flush(self):
        self.flushed = True

    def reset(self):
        self.reset_called = True


def test_callbacks_methods():
    mock_callback1 = MockCallback()
    mock_callback2 = MockCallback()
    callbacks = Callbacks([mock_callback1, mock_callback2])
    mock_publisher = MagicMock(spec=Publisher)

    callbacks.set('example_attr', 'test_value')
    assert getattr(mock_callback1, 'example_attr') == 'test_value'
    assert getattr(mock_callback2, 'example_attr') == 'test_value'

    callbacks.bind(mock_publisher)
    assert mock_callback1.publisher == mock_publisher
    assert mock_callback2.publisher == mock_publisher

    callbacks('arg1', key='value')
    assert mock_callback1.called is True
    assert mock_callback2.called is True

    callbacks.flush()
    assert mock_callback1.flushed is True
    assert mock_callback2.flushed is True

    callbacks.reset()
    assert mock_callback1.reset_called is True
    assert mock_callback2.reset_called is True
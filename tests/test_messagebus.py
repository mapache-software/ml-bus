from pybondi.messagebus import Messagebus
from pybondi.events import Added, Saved

messagebus = Messagebus()

@messagebus.on(Added, Saved)
def handle_events(event):
    pass

def test_messagebus():
    assert messagebus.event_handlers[Added][0] == handle_events
    assert messagebus.event_handlers[Saved][0] == handle_events
from pybondi.messagebus import Messagebus
from pybondi.events import Added, Commited

messagebus = Messagebus()

@messagebus.subscribe(Added, Commited)
def handle_events(event):
    pass

def test_messagebus():
    assert messagebus.event_handlers[Added][0] == handle_events
    assert messagebus.event_handlers[Commited][0] == handle_events
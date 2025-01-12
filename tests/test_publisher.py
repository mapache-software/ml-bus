from pybondi.publisher import Publisher, Depends

publisher = Publisher()
nfs = []
db = []

def get_db():
    return db

@publisher.subscriber('topic-1', 'topic-2')
def callback(message):
    nfs.append(message)

@publisher.subscriber('topic-2')
def second_callback(message, db = Depends(get_db)):
    print(message)
    db.append(message)
    
def test_publisher():
    publisher.publish('topic-1', 'Hello')
    publisher.publish('topic-2', 'World')
    assert db == ['World']
    assert nfs == ['Hello', 'World']
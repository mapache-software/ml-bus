from abc import ABC, abstractmethod
from typing import Any
from typing import Sequence
from pybondi.publisher import Publisher

class Callback(ABC):
    '''
    Usually a domain object publish an event and the data from that event is processed
    and sent to external system using a publisher. But sometimes the data needs to be
    published just after it is processed. In such cases, the domain object can use a 
    callback object to process the data and publish it immediately.

    Callbacks should be injected into the aggregate's methods to allow it to process
    data and communicate their results to the message publisher.

    When a callback is passed to an aggregate's it shouldn't know that a complex comunication
    object is being used. It should just call the callback object as if it were a function.
    '''

    def __init__(self):
        self.publisher = Publisher()

    def bind(self, publisher: Publisher):
        '''
        Bind a publisher to the callback object.        
        '''
        self.publisher = publisher

    def set(self, name: str, value: Any) -> None:
        '''
        Set a value on the callback object.

        Paramaters:
            name: The name of the attribute.
            value: The value to set.       
        '''
        setattr(self, name, value)

    @abstractmethod
    def __call__(self, *args, **kwargs):
        '''
        Call the callback object. Data from the aggregate's methods should be passed
        to the callback object through this method, and processed accordingly.

        The callback object should also communicate the results of the processing to
        the message publisher directly or should implement a buffer to store the results
        until the flush method is called.        
        '''
        ...

    @abstractmethod
    def flush(self): 
        '''
        Flush the callback object. If the callback object has a buffer, the buffer should
        be flushed and the data should be sent to the message publisher.    
        '''
        ...

    @abstractmethod
    def reset(self):
        '''
        Reset the callback object. The callback object should reset any internal state
        that it maintains, if any.
        '''
        ...

class Callbacks:
    '''
    Callbacks is a class that manages a group of callback objects. It is responsible for
    calling the callback objects, flushing their buffers, and resetting their internal
    state, as if they were a single callback object.

    Example:

    callback = Callbacks([SomeCallback(), OtherCallback())
    '''

    def __init__(self, callbacks: Sequence[Callback]):
        self.publisher = Publisher()
        self.list = list[Callback](callbacks)
        for callback in self.list:
            callback.bind(self.publisher) 
    
    def bind(self, publisher: Publisher):
        '''
        Bind a publisher to all the callback objects.
        '''
        self.publisher = publisher
        [callback.bind(publisher) for callback in self.list]

    def set(self, name: str, value: Any) -> None:
        '''
        Set a value to all the callback objects.

        Paramaters:
            name: The name of the attribute.
            value: The value to set.       
        '''
        [callback.set(name, value) for callback in self.list]


    def __call__(self, *args, **kwargs):
        '''
        Call the callbacks. Data from the aggregate's methods should be passed
        to the callback objects through this method, and processed accordingly.   
        '''
        for callback in self.list:
            callback(*args, **kwargs)

    def flush(self):
        '''
        Flush the callbacks. If the callback objects have a buffer, the buffer should
        be flushed and the data should be sent to the message publisher.    
        '''
        for callback in self.list:
            callback.flush()
        
    def reset(self):
        '''
        Reset the callbacks. The callback objects should reset any internal state
        that they maintain, if any.
        '''
        for callback in self.list:
            callback.reset()
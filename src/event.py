#!/usr/bin/env python
"""Examples at the end of the module"""


class EventHandler:
    """Calls the set of functions that handle a given event.
    
    You don't need to register events. You can EventHandler.handle('whatever')
    """

    # A tuple so that unbind and emit won't crash
    # bind will make it a dictionary, making it useful
    _eventBindings = ()

    def register(self, *events):
        if type(self._eventBindings) is tuple:
            self._eventBindings = {}
        for event in events:
            self._eventBindings[event] = set()

    def bind(self, event, function):
        assert event in self._eventBindings
        self._eventBindings[event].add(function)

    def unbind(self, event, function):
        assert event in self._eventBindings
        if function in self._eventBindings[event]:
            self._eventBindings[event].remove(function)

    def emit(self, event, *args):
        assert event in self._eventBindings
        for function in self._eventBindings[event]:
            function(*args)

    def __repr__(self):
        return "<EventHandler instance binding %s>" % str(self._eventBindings)


if __name__ == "__main__":
    eventHandler = EventHandler()

    def sayHi():
        print("Hi!")

    eventHandler.register("anEvent")
    eventHandler.bind("anEvent", sayHi)
    eventHandler.emit("anEvent")
    # Error example
    # eventHandler.emit('an_event', 4, 3, 1) #Error! Wrong argument amount

    def goat(arg0, arg1, arg2):
        print(arg0, arg1, arg2)

    eventHandler.register("goat")
    eventHandler.bind("goat", goat)
    eventHandler.emit("goat", 4, "hello", 9)
    eventHandler.unbind("goat", goat)
    eventHandler.emit("goat", 1, 24, 7)
    eventHandler.emit("goat", "peeper")  # Would crash if goat were to handle the event.
    print(eventHandler)


import fnmatch
import copy

class Events:
    def __init__(self):
        self.listeners = []

    def call(self, event, *args, **kwargs):
        for listener in self.listeners:
            _kwargs = copy.copy(kwargs)

            if "*" in listener.event:
                _kwargs["__event__"] = event

            if fnmatch.filter([event], listener.event):
                listener.callback(*args, **_kwargs)

    def _hook(self, event, callback):
        listener = Listener(event, callback)
        self.listeners.append(listener)

    def hook(self, event):
        def wrap(func):
            self._hook(event, func)

        return wrap

class Listener:
    def __init__(self, event, callback):
        self.event = event
        self.callback = callback

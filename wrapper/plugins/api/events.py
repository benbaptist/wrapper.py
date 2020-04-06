import fnmatch
import copy

class Events:
    def __init__(self, api):
        self.api = api
        self._wrapper = api._wrapper
        self._events = self._wrapper.events

        self.listeners = []

        self._events._hook("*", self._callback)

    def _callback(self, *args, **kwargs):
        if not self.api._plugin._main:
            return

        event = kwargs["__event__"]

        for listener in self.listeners:
            if fnmatch.filter([event], listener.event):
                try:
                    listener.callback(*args, **kwargs)
                except TypeError:
                    _kwargs = copy.copy(kwargs)
                    del _kwargs["__event__"]

                    listener.callback(*args, **_kwargs)

    def hook(self, event):
        def wrap(func):
            listener = Listener(event, func)
            self.listeners.append(listener)

        return wrap

class Listener:
    def __init__(self, event, callback):
        self.event = event
        self.callback = callback

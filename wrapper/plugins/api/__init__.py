from wrapper.plugins.api.minecraft import Minecraft
from wrapper.plugins.api.events import Events

class API:
    def __init__(self, wrapper, plugin):
        self._wrapper = wrapper
        self._plugin = plugin

        # Expose existing internal API(s)
        self.server = self._wrapper.server

        # Expose proper APIs made for plugins
        self.minecraft = Minecraft(self)
        self.events = Events(self)

    def __disable__(self):
        self.minecraft.__disable__()

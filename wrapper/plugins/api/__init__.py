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

    @property
    def storage(self):
        # Expose storage API
        try:
            return self._storage
        except:
            self._storage = self._wrapper.storify.getDB("plugin_%s" % self._plugin.id)
            return self._storage

    def __disable__(self):
        self.minecraft.__disable__()

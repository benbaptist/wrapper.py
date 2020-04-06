from wrapper.plugins.api.minecraft import Minecraft

class API:
    def __init__(self, wrapper, plugin):
        self._wrapper = wrapper
        self._plugin = plugin

        # Expose existing internal APIs
        # This is temporary.
        self.server = self._wrapper.server
        self.events = self._wrapper.events

        # Expose proper APIs made for plugins
        self.minecraft = Minecraft(self)

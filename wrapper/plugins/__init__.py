import os

from wrapper.plugins.plugin import Plugin

class Plugins:
    def __init__(self, wrapper):
        self.wrapper = wrapper
        self.log = wrapper.log_manager.get_logger("plugins")
        self.db = wrapper.storify.getDB("plugins")

        self.plugins = []

        if not os.path.exists("wrapper-data/plugins"):
            os.makedirs("wrapper-data/plugins")

    def load_plugins(self):
        for path in os.listdir("wrapper-data/plugins"):
            try:
                name, ext = path.rsplit(".", 1)
            except:
                name, ext = path, None

            if os.path.isdir(path):
                if not os.path.join(path, "__init__.py"):
                    continue
            else:
                if ext != "py":
                    continue

                if name[0] == ".":
                    continue

            path = os.path.join("wrapper-data/plugins", path)

            self.load_plugin(path)

    def load_plugin(self, path):
        self.log.debug("Loading plugin '%s'" % path)
        plugin = Plugin(self.wrapper, path)
        plugin.load()

        self.plugins.append(plugin)

    def unload_plugins(self):
        for plugin in self.plugins:
            plugin.unload()

        self.plugins = []

    def reload_plugins(self):
        self.unload_plugins()
        self.load_plugins()

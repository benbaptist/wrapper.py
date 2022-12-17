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
        IGNORE = ["__pycache__"]

        for path in os.listdir("wrapper-data/plugins"):

            if path in IGNORE:
                continue

            try:
                name, ext = path.rsplit(".", 1)
            except:
                name, ext = path, None

            path = os.path.join("wrapper-data/plugins", path)
            plugin_name = None

            if os.path.isdir(path):
                if not os.path.join(path, "__init__.py"):
                    continue
                else:
                    plugin_name = name
            else:
                if ext != "py":
                    continue

                if name[0] == ".":
                    continue

            self.load_plugin(path, plugin_name)

    def load_plugin(self, path, name):
        self.log.debug("Loading plugin '%s'" % path)
        plugin = Plugin(self.wrapper, path, name)
        plugin.load()

        self.plugins.append(plugin)

    def unload_plugins(self):
        for plugin in self.plugins:
            plugin.unload()

        self.plugins = []

    def reload_plugins(self):
        self.unload_plugins()
        self.load_plugins()

    def disable_plugin(self, plugin_id):
        return

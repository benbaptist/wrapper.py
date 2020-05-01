try:
    # Python 2.x
    import imp
except DeprecationWarning:
    # Python 3.5+
    imp = None
    import importlib.util

import os

from wrapper.plugins.api import API

class Plugin:
    def __init__(self, wrapper, path):
        self.wrapper = wrapper

        if os.path.isdir(path):
            self.path = os.path.join(path, "__init__.py")
        else:
            self.path = path

        self.name = os.path.basename(self.path)
        self.success = None
        self._main = None

        self.log = self.wrapper.log_manager.get_logger("plugin/%s" % self.name)

        self._api = API(self.wrapper, self)

    def _import(self):
        module_name = "wrapper.plugin.%s" % self.name

        if imp:
            # Python 2.x
            module = imp.load_source(module_name, self.path)

            return module
        else:
            # Python 3.x
            spec = importlib.util.spec_from_file_location(
                module_name, self.path
            )

            module = importlib.util.module_from_spec(spec)

            spec.loader.exec_module(module)

            return module

        raise ImportError("Failed to import plugin")

    def load(self):
        try:
            self.module = self._import()
            self.id = getattr(self.module, "ID", self.name)

            self._main = self.module.Main(self._api, self.log)
            self._main.__enable__()

            self.success = True
        except:
            self.log.traceback("Failed to load plugin")
            self.success = False
            self._main = None

    def unload(self):
        if self._main:
            try:
                self._main.__disable__()
                self._main = None

                self._api.__disable__()
            except:
                self.log.traceback("Failed to unload plugin")

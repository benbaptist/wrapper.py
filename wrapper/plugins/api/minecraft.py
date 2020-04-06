class Minecraft:
    def __init__(self, api):
        self._api = api
        self._wrapper = api._wrapper
        self._server = api._wrapper.server
        self._plugin = api._plugin

    def __disable__(self):
        self._server.commands.unregister_domain(self._plugin.id)

    def command(self, command, permission=None):
        def wrap(func):
            self._server.commands._register(command, func, permission, self._plugin.id)

        return wrap

    def permission(self, permission):
        return

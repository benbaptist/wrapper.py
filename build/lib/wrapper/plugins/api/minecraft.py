from wrapper.server.commands import Command

class Minecraft:
    def __init__(self, api):
        self._api = api
        self._wrapper = api._wrapper
        self._server = api._wrapper.server
        self._plugin = api._plugin

        self._plugin.commands = []

    def __disable__(self):
        return
        # self._server.commands.unregister_domain(self._plugin.id)

    def command(self, name, permission=None):
        """ Register a command to a Python method through a decorator """
        def wrap(callback):
            self._plugin.commands.append(
                Command(
                    name,
                    callback,
                    permission
                )
            )
            # self._plugin.commands[command] = {
            #     "func": func,
            #     "permission": permission
            # }
            # self._server.commands._register(command, func, permission, self._plugin.id)

        return wrap

    def unregister_command(self, command):
        """ Unregister a command """
        if command in self._plugin.commands:
            del self._plugin.commands[command]

    def permission(self, permission):
        return

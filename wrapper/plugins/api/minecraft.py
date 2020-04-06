class Minecraft:
    def __init__(self, api):
        self.api = api
        self.wrapper = api._wrapper
        self.plugin = api._plugin

    def command(self, command, permission=None):
        def wrap(func):
            raise Exception("Unimplemented")

        return wrap

    def permission(self, permission):
        return

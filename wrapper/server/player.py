import json

class Player:
    def __init__(self, server, username, mcuuid, online_mode=None):
        self.server = server
        self.mojang = server.wrapper.mojang
        self.username = username
        self.mcuuid = mcuuid

        self.position = None
        self.ip_address = None
        self.entity_id = None
        self.online = False

        self._callbacks = {
            "poll_position": []
        }

        if online_mode in (False, True):
            self.online_mode = online_mode
        else:
            self.online_mode = self.server.online_mode

        if self.online_mode:
            self.skin = self.mojang.get_skin_from_uuid(self.mcuuid)
        else:
            self.skin = None

    def __serialize__(self):
        return {
            "username": self.username,
            "mcuuid": str(self.mcuuid),
            "ip_address": self.ip_address,
            "skin": self.skin
        }

    def _poll_position(self):
        self.server.run("execute at %s run tp %s ~ ~ ~"
            % (self.username, self.username)
        )

    def _callback(self, method, *args):
        # this is stupid
        for callback in self._callbacks[method]:
            callback(*args)

        self._callbacks[method] = []

    def message(self, message):
        """ Sends a /tellraw message to this player. """
        self.server.features.message(self.username, message)

    def message_as_player(self, message):
        """ Simulates sending a message as this player. """
        self.server.log.info("<%s> %s" % (self.username, message))
        self.server.broadcast("<%s> %s" % (self.username, message))

    def kick(self, reason="Kicked from server"):
        self.server.run(
            "kick %s %s"
            % (self.username, reason)
        )

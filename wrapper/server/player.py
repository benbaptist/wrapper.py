class Player:
    def __init__(self, server, username, mcuuid, online_mode=None):
        self.server = server
        self.mojang = server.wrapper.mojang
        self.username = username
        self.mcuuid = mcuuid

        self.position = None
        self.ip_address = None
        self.entity_id = None

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

    def message(self, message):
        """ Simulates sending a message as this player. """
        self.server.log.info("<%s> %s" % (self.username, message))
        self.server.broadcast("<%s> %s" % (self.username, message))

    def kick(self, reason="Kicked from server"):
        self.server.command(
            "kick %s %s"
            % (self.username, {
                "text": reason
            })
        )

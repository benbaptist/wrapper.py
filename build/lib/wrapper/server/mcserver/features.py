import json

class Features:
    """ This is an abstraction layer to automatically determine the best
    commands (and their syntax) for each version of Minecraft. """

    def __init__(self, mcserver):
        self.mcserver = mcserver

    @property
    def version(self):
        if self.mcserver.server_version_protocol:
            return self.mcserver.server_version_protocol
        else:
            # Unknown server version; treat as "newest"
            return 77

    def __run__(self, cmd):
        self.mcserver.command(cmd)

    def stop(self):
        """ Tells the server to shutdown cleanly. """
        self.__run__("stop")

    def message(self, target, message):
        """ Message player(s) with a given message. """
        if self.version >= 76:
            # Use /tellraw

            if type(message) != dict:
                message = {
                    "text": message
                }

            message = json.dumps(message)

            self.__run__(
                "tellraw %s %s" % (target, message)
            )
        else:
            # TO-DO: convert message from JSON to string, if neccessary
            if target == "@a":
                # Use /say
                self.__run__(
                    "say %s" % message
                )
            else:
                # Use /tell
                self.__run__(
                    "tell %s %s" % (target, message)
                )

    def play_sound(self):
        raise NotImplemented()

    def set_block(self):
        raise NotImplemented()

    def fill(self):
        raise NotImplemented()

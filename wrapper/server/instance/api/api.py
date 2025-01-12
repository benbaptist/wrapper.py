import json
from .types import Message

class API:
    """ This is an abstraction layer to automatically determine the best
    commands (and their syntax) for each version of Minecraft. """

    def __init__(self, instance):
        self.instance = instance

    @property
    def version(self):
        return 77
    
        if self.instance.server.server_version_protocol:
            return self.instance.server.server_version_protocol
        else:
            # Unknown server version; treat as "newest"
            return 77

    def _run(self, cmd):
        self.instance.run(cmd)

    def kick(self, target, reason=None):
        """ Kick a player from the server. """
        self._run(f"kick {target} {reason}")

    def stop(self):
        """ Tells the server to shutdown cleanly. """
        try:
            self._run("stop")
        except ServerStopped:
            pass

    def title(self, message, target="@a", title_type="title", fade_in=None, stay=None, fade_out=None):
        """ Send a title to a player. """
        if len(self.players) < 1:
            return

        if fade_in or stay or fade_out:
            pass

        if isinstance(message, Message):
            json_blob = json.dumps(message.json)
        else:
            json_blob = json.dumps(Message(text=message).json)

        self.run(f"title {target} {title_type} {json_blob}")

    def message(self, target, message):
        """ Message player(s) with a given message. """
        if type(message) == str:
            message = Message(text=message)

        if self.version >= 76:
            # Use /tellraw
            message = json.dumps(message.json)

            self._run(f"tellraw {target} {message}")
        else:
            if target == "@a":
                # Use /say
                self._run(f"say {message.legacy}")
            else:
                # Use /tell
                self._run(f"tell {target} {message.legacy}")

    def play_sound(self):
        raise NotImplemented()

    def set_block(self):
        raise NotImplemented()

    def fill(self):
        raise NotImplemented()

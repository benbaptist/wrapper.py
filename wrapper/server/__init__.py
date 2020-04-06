import json

from uuid import UUID

from wrapper.server.mcserver import MCServer
from wrapper.server.player import Player
from wrapper.server.commands import Commands
from wrapper.exceptions import *
from wrapper.commons import *

class Server(object):
    def __init__(self, wrapper):
        self.wrapper = wrapper
        self.events = wrapper.events

        self.log = wrapper.log_manager.get_logger("server")
        self.db = wrapper.db

        if "server" not in self.db:
            self.db["server"] = {
                "state": SERVER_STARTED # SERVER_STARTED/SERVER_STOPPED
            }

        self.mcserver = None

        # Dummy player used for console user
        self._console_player = Player(
            self,
            username="$Console$",
            mcuuid=UUID(bytes=bytes(bytearray(16))),
            online_mode=False
        )

        # Commands handler
        self.commands = Commands(self)

    @property
    def state(self):
        if self.mcserver:
            return self.mcserver.state
        else:
            return SERVER_STOPPED

    @property
    def players(self):
        if self.mcserver:
            return self.mcserver.players

    @property
    def world(self):
        if self.mcserver:
            return self.mcserver.world

    @property
    def online_mode(self):
        if self.mcserver:
            return self.mcserver.online_mode

    def broadcast(self, message):
        if len(self.players) < 1:
            return

        if type(message) == dict:
            json_blob = json.dumps(message)
        else:
            json_blob = json.dumps({
                "text": message
            })

        self.command("tellraw @a %s" % json_blob)

    def title(self, message, target="@a", title_type="title", fade_in=None, stay=None, fade_out=None):
        if len(self.players) < 1:
            return

        if fade_in or stay or fade_out:
            pass

        if type(message) == dict:
            json_blob = json.dumps(message)
        else:
            json_blob = {
                "text": message
            }
            json_blob = json.dumps(json_blob)

        self.command(
            "title %s %s %s"
            % (target, title_type, json_blob)
        )

    def command(self, cmd):
        if self.mcserver:
            self.mcserver.command(cmd)

    def start(self):
        self.db["server"]["state"] = SERVER_STARTED

    def restart(self, reason="Server restarting"):
        if self.mcserver:
            for player in self.players:
                player.kick(reason)

            self.mcserver.abort = True

        self.start()

    def stop(self, reason="Server stopping", save=True):
        if self.mcserver:
            self.mcserver.stop()

            for player in self.players:
                player.kick(reason)

        if save:
            self.db["server"]["state"] = SERVER_STOPPED

    def kill(self):
        if self.mcserver:
            self.mcserver.kill()

    def tick(self):
        if not self.mcserver:
            if self.db["server"]["state"] == SERVER_STARTED:
                self.mcserver = MCServer(self.wrapper, self)

        if self.mcserver:

            try:
                self.mcserver.tick()
            except ServerStopped:
                self.mcserver = None

                self.log.info("Server stopped")
                self.events.call("server.stopped")
                return

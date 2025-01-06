import json
import time
import os

from .instance import Instance
from .player import Player
from .commands import Commands
from .log import Log
from ..exceptions import *
from ..commons import *

class Server(object):
    """
    Represents general server operations, such as starting, stopping, restarting, etc. and manages the currently running server instance
    """
    def __init__(self, wrapper):
        self.wrapper = wrapper
        self.events = wrapper.events

        self.log = wrapper.log_manager.get_logger("server")
        self.db = wrapper.db

        if "server" not in self.db:
            self.db["server"] = {
                "state": SERVER_STARTED # SERVER_STARTED/SERVER_STOPPED
            }

        self.instance = None
        self._timeout = 0

        # Commands handler
        self.commands = Commands(self)

        # Event handlers
        @self.events.hook("server.reload")
        def reload(player):
            if player:
                player.message({
                    "text": "Server reloading",
                    "color": "yellow"
                })

                self.log.info(
                    "Server being reloaded by %s, triggering plugin reload"
                    % player.username
                )
            else:
                self.log.info(
                    "Server being reloaded, triggering plugin reload"
                )

            self.wrapper.plugins.reload_plugins()

        @self.events.hook("server.player.command_response")
        def response(player, command_response):
            print(player, command_response)
            player.message(command_response)

    @property
    def state(self):
        if self.instance:
            return self.instance.state
        else:
            return SERVER_STOPPED

    @property
    def all_players(self):
        if self.instance:
            return self.instance.list_players(everyone=True)

        return []

    @property
    def players(self):
        if self.instance:
            online_players = []

            for player in self.instance.players:
                if player.online:
                    online_players.append(player)

            return online_players

    def get_player(self, username=None, mcuuid=None, ip_address=None):
        for player in self.instance.players:
            if username:
                if username == player.username:
                    return player

            if mcuuid:
                if player.mcuuid == mcuuid:
                    return player

            if ip_address:
                if player.ip_address == ip_address:
                    return player

        raise PlayerNotFound("Player by criteria %s/%s/%s not found" % (username, mcuuid, ip_address))

    def get_player_(self, mcuuid):
        for player in self.all_players:
            if str(player.mcuuid) == mcuuid:
                return player

    @property
    def logs(self):
        files = os.listdir("logs")
        files.sort()

        log_files = []

        for fn in files:
            try:
                name, ext = fn.rsplit(".", 1)
            except:
                name,  ext = fn, None

            log = Log(fn)

            if ext in ("gz", "log"):
                log_files.append(log)

        return log_files

    def broadcast(self, message):
        # TODO: Move to instance object
        if len(self.players) < 1:
            return

        self.instance.features.message("@a", message)

    def title(self, message, target="@a", title_type="title", fade_in=None, stay=None, fade_out=None):
        # TODO: Move to instance object
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

        self.run(
            "title %s %s %s"
            % (target, title_type, json_blob)
        )

    def run(self, cmd, output=False):
        if self.instance:
            self.instance.command(cmd)

    def start(self):
        self.db["server"]["state"] = SERVER_STARTED

    def restart(self, reason="Server restarting"):
        if self.instance:
            for player in self.players:
                player.kick(reason)

            time.sleep(.1)

            self.instance.stop()
            self.db["server"]["state"] = SERVER_RESTART

    def stop(self, reason="Server closed", save=True):
        if self.instance:
            for player in self.players:
                player.kick(reason)

            self.instance.stop()

        time.sleep(.1)

        if save:
            self.db["server"]["state"] = SERVER_STOPPED

    def kill(self):
        if self.instance:
            self.instance.kill()

    def tick(self):
        if not self.instance:
            if self.db["server"]["state"] == SERVER_RESTART:
                self.db["server"]["state"] = SERVER_STARTED

            if self.db["server"]["state"] not in (SERVER_RESTART, SERVER_STARTED):
                return

            server_jar = self.wrapper.config["server"]["jar"]

            if not os.path.exists(server_jar):
                self.log.error("Server jar '%s' does not exist" % server_jar)

                self.db["server"]["state"] = SERVER_STOPPED
                return

            self.instance = Instance(self.wrapper, self)
            return

        if self.instance:
            try:
                self.instance.tick()
            except ServerStopped:
                self.instance = None

                self.log.info("Server stopped")
                self.events.call("server.stopped")

                # Check if wrapper is shutting down too
                if not self.wrapper.initiate_shutdown:

                    # If server was in restart state, move along and let it start
                    if self.db["server"]["state"] == SERVER_RESTART:
                        return

                    # If auto-restart is off, don't let server restart itself
                    if not self.wrapper.config["server"]["auto-restart"]:
                        self.db["server"]["state"] = SERVER_STOPPED

                return

            # If timed reboot is enabled, check server uptime and reboot
            if self.wrapper.config["server"]["timed-reboot"]["enable"]:
                uptime_seconds = time.time() - self.instance._start_time
                warning_seconds = self.wrapper.config["server"]\
                    ["timed-reboot"]["warning-seconds"]
                interval_seconds = self.wrapper.config["server"]\
                    ["timed-reboot"]["interval-seconds"]

                if self.state == SERVER_STARTED:
                    if uptime_seconds >= interval_seconds:
                        self.log.info("Timed reboot initiated")
                        self.restart()

            # Poll every 200ms
            if time.time() - self._timeout > .2:
                for player in self.players:
                    pass

                self._timeout = time.time()

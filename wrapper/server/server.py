import json
import time
import os

from .instance import Instance
from .instance.player import Player
from .instance.commands import Commands
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
        # TODO: Move to instance object
        self.commands = Commands(self)

        # Event handlers
        # TODO: Move to instance object
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

    def start(self):
        self.db["server"]["state"] = SERVER_STARTED

    def restart(self, reason="Server restarting"):
        if self.instance:
            for player in self.instance.players:
                player.kick(reason)

            time.sleep(.1)

            self.instance.stop()
            self.db["server"]["state"] = SERVER_RESTART

    def stop(self, reason="Server closed", save=True):
        if self.instance:
            for player in self.instance.players:
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

            self.instance = Instance(self)
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
                self._timeout = time.time()

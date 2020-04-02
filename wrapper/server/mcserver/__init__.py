import json
import uuid
import time
import os
import resource

from wrapper.server.process import Process
from wrapper.server.player import Player
from wrapper.server.uuid_cache import UUID_Cache
from wrapper.server.mcserver.console_parser import ConsoleParser
from wrapper.commons import *
from wrapper.exceptions import *

class MCServer:
    def __init__(self, wrapper):
        self.wrapper = wrapper
        self.events = wrapper.events
        self.config = wrapper.config
        self.log = wrapper.log_manager.get_logger("mcserver")

        self.process = None

        self.state = SERVER_STOPPED
        self.target_state = (SERVER_STOPPED, time.time())

        self.uuid_cache = UUID_Cache()
        self.console_parser = ConsoleParser(self)

        self._reset()

        self._timeout = 0

        self._chat_scrollback = []
        self._resource_analytics = []

        # Dummy player used for console user
        self._console_player = Player(
            username="$Console$",
            mcuuid=uuid.UUID(bytes=bytes(16))
        )

    def _reset(self):
        self.players = []
        self.world = None
        self.server_version = None
        self.server_port = None

        self.process = None
        self.dirty = False

    def start(self):
        if self.state != SERVER_STOPPED:
            raise StartingException("Server is already running")

        self.log.info("Starting server")

        # Call event
        self.events.call("server.starting")

        # Check EULA
        agree_eula = False
        if os.path.exists("eula.txt"):
            with open("eula.txt", "r") as f:
                if not "eula=true" in f.read():
                    agree_eula = True
        else:
            agree_eula = True

        if agree_eula:
            with open("eula.txt", "w") as f:
                f.write("eula=true")

        self._reset()

        # Start process
        custom_java_bin = self.config["server"]["custom-java-bin"]
        if not custom_java_bin:
            custom_java_bin = "java"

        self.process = Process()
        self.process.start(self.config["server"]["jar"], java_bin=custom_java_bin)
        self.state = SERVER_STARTING

        self.target_state = (SERVER_STARTED, time.time())

    # Control server states
    def stop(self, reason):
        self.target_state = (SERVER_STOPPED, time.time())

    def restart(self, reason):
        self.target_state = (SERVER_RESTART, time.time())

    def freeze(self):
        return

    def unfreeze(self):
        return

    def kill(self):
        self.process.kill()

    # Commands
    def run_command(self, cmd):
        if not self.process:
            raise ServerStopped()

        self.process.write("%s\n" % cmd)

    def broadcast(self, msg):
        if type(msg) == dict:
            json_blob = json.dumps(msg)
        else:
            json_blob = json.dumps({
                "text": msg
            })
        self.run_command("tellraw @a %s" % json_blob)

    # Players
    def list_players(self):
        players = []

        for player in self.players:
            # Filters go here

            players.append(player)

        return players

    def get_player(self, username=None, mcuuid=None, ip_address=None):
        for player in self.players:
            if username:
                if username == player.username:
                    return player

            if mcuuid:
                if player.uuid == mcuuid:
                    return player

            if ip_address:
                if player.ip_address == ip_address:
                    return player

    # Server stuff
    def get_ram_usage(self):
        if not self.process:
            raise ServerStopped("Server not running")

        return self.process.get_ram_usage()

    def get_cpu_usage(self):
        if not self.process:
            raise ServerStopped("Server not running")

        return self.process.get_cpu_usage()

    # Tick
    def tick(self):
        # Check if server process is stopped
        if self.process:
            if not self.process.process:
                self._reset()

        if not self.process and self.state != SERVER_STOPPED:
            # print("self.process is dead, state == server-stopped")
            self.log.info("Server stopped")
            self.state = SERVER_STOPPED
            self.events.call("server.stopped")
            self._reset()

        # Check target state, and do accordingly
        target_state, target_state_time = self.target_state
        if target_state in (SERVER_STOPPED, SERVER_RESTART):

            # Start server shutdown, if it hasn't already started
            if self.state not in (SERVER_STOPPING, SERVER_STOPPED):
                self.run_command("stop")
                self.state = SERVER_STOPPING

            # Check if server stop has been going for too long, and kill server
            if self.state == SERVER_STOPPING:
                if time.time() - target_state_time > 60:
                    self.kill()

            # Check if server is fully stopped, and then start it again
            if target_state == SERVER_RESTART and self.state == SERVER_STOPPED:
                self.start()

        # Don't go further unless a server process exists
        if not self.process:
            return

        # Get server resource usage every second
        if time.time() - self._timeout > 1:
            ram_usage = self.get_ram_usage()
            self.events.call("server.status.ram", usage=ram_usage)

            cpu_usage = self.get_cpu_usage()
            self.events.call("server.status.cpu", usage=cpu_usage)

            self._timeout = time.time()

        # Check if server is 'dirty'
        if len(self.players) > 0:
            self.dirty = True

        # Regex new lines
        for std, line in self.process.console_output:
            # Print line to console
            print(line)

            self.console_parser.parse(line)

        # Dirty hack, let's make this better later using process.read_console()
        self.process.console_output = []

import json
import uuid
import time
import os
import resource

from wrapper.server.player import Player
from wrapper.server.uuid_cache import UUID_Cache
from wrapper.server.mcserver.process import Process
from wrapper.server.mcserver.console_parser import ConsoleParser
from wrapper.server.mcserver.features import Features
from wrapper.commons import *
from wrapper.exceptions import *

class MCServer:
    def __init__(self, wrapper, server):
        self.wrapper = wrapper
        self.server = server
        self.events = wrapper.events
        self.config = wrapper.config
        self.log = wrapper.log_manager.get_logger("mcserver")

        self.players = []
        self.world = None
        self.server_version = None
        self.server_version_protocol = None
        self.port = None
        self.online_mode = True
        self.gamerules = {
            "sendCommandFeedback": True,
            "logAdminCommands": True
        }

        self.features = Features(self)

        self.process = None
        self.abort = False
        self.state = SERVER_STARTING

        self.uuid_cache = UUID_Cache()
        self.console_parser = ConsoleParser(self)

        self._timeout = 0

        self._resource_analytics = []

        self._start()

    def _start(self):
        self.log.info("Starting server")

        # Call event
        self.events.call("server.starting")

        # Check EULA, and agree with it
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

        # Start process
        custom_java_bin = self.config["server"]["custom-java-bin"]
        if not custom_java_bin:
            custom_java_bin = "java"

        if len(self.config["server"]["arguments"]) > 0:
            arguments = self.config["server"]["arguments"].split(" ")
        else:
            arguments = []

        if self.config["server"]["cmd"]:
            command = self.config["server"]["cmd"].split(" ")
        else:
            command = None

        server_jar = self.config["server"]["jar"]

        self.process = Process()
        self.process.start(
            jar_name=server_jar,
            java_args=arguments,
            java_bin=custom_java_bin,
            command=command
        )

        self.state = SERVER_STARTING

    # Control server states
    def stop(self):
        self.abort = time.time()

    def freeze(self):
        return

    def unfreeze(self):
        return

    def kill(self):
        self.process.kill()
        self.process = None
        self.state = SERVER_STOPPED

    # Commands
    def command(self, cmd):
        if not self.process:
            raise ServerStopped()

        self.process.write("%s\n" % cmd)

    # Players
    def list_players(self, online=True, everyone=False):
        """ Returns a list containing all players.
        Defaults to online-only. """
        players = []

        # Load offline players before we begin
        for player_data_path in os.listdir("wrapper-data/players"):
            try:
                name, ext = player_data_path.rsplit(".", 1)
            except:
                continue

            if ext != "mpack":
                continue

            mcuuid = uuid.UUID(name)

            try:
                self.server.get_player(mcuuid=mcuuid)
            except TypeError:
                player = Player(
                    server=self.server,
                    mcuuid=mcuuid
                )

                self.players.append(player)
                print("Adding player %s" % player)

        # Filter players
        for player in self.players:

            if not everyone:
                # Future criteria filters should go here
                if online and not player.online:
                    continue
                elif online == False and player.online:
                    continue

            players.append(player)

        return players

    # Tick
    def tick(self):
        # Check if server process is stopped
        if self.process:
            if not self.process.process:
                self.state = SERVER_STOPPED
        else:
            self.state = SERVER_STOPPED

        # Don't go further unless a server process exists
        if self.state == SERVER_STOPPED:
            for player in self.players:
                if player.online:
                    self.events.call(
                        "server.player.part",
                        player=player
                    )

            raise ServerStopped()

        if self.abort:
            # Start server stop, if it hasn't already started
            if self.state == SERVER_STARTED:
                self.features.stop()
                self.state = SERVER_STOPPING

            # Check if server stop has been going for too long, and kill server
            if time.time() - self.abort > 60:
                self.kill()
                return

        # Get server resource usage every second
        if time.time() - self._timeout > 1:
            self.ram_usage = self.process.get_ram_usage()
            self.events.call("server.status.ram", usage=self.ram_usage)

            self.cpu_usage = self.process.get_cpu_usage()
            self.events.call("server.status.cpu", usage=self.cpu_usage)

            self._timeout = time.time()

        # Process server output
        for std, line in self.process.read_console():
            # Parse line
            if self.console_parser.parse(line) != False:
                # Print line to console
                print(line)

            # Call event for line
            self.events.call("server.console.output", line=line)

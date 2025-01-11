import uuid
import time
import os

from .player import Player
from .uuid_cache import UUID_Cache
from .process import Process
from .parser import LogParser, Handler
from .api import API
from ...commons import *
from ...exceptions import *

class Instance:
    """
    Represents the server instance; expected lifespan is during the server's uptime; rebooting or stopping the server will destroy this object

    Duties include abstracting the server and its console output into a consistent interface, and managing the server's features
    """
    def __init__(self, server):
        self.server = server
        self.events = server.wrapper.events
        self.config = server.wrapper.config
        self.log = server.wrapper.log_manager.get_logger("instance")

        self._players = []
        self.world = None
        self.server_version = None
        self.server_version_protocol = None
        self.port = None
        self.online_mode = True
        self.gamerules = {
            "sendCommandFeedback": True,
            "logAdminCommands": True
        }

        self.process = Process()
        self.abort = False
        self.state = SERVER_STARTING

        self.api = API(self)
        self.uuid_cache = UUID_Cache()
        self.parser = LogParser()
        self.handler = Handler(self)
        self._timeout = 0

        self._resource_analytics = []

        self._start_time = time.time()

        self._start()

    def _agree_eula(self):
        # Check EULA, and automatically agree with it
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

    def _start(self):
        self.log.info("Starting server")

        # Call start event
        self.events.call("server.starting")

        # Agree to EULA
        self._agree_eula()

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

        self.process.start(
            jar_name=server_jar,
            java_args=arguments,
            java_bin=custom_java_bin,
            command=command
        )

        self.java_version = self.process.java_version

        self.log.info("Java Version: %s" % self.java_version)

        self.state = SERVER_STARTING

    # Control server states
    def stop(self):
        """ Stops the server """
        self.abort = time.time()

    def freeze(self):
        """ Freezes the server """
        raise NotImplementedError("Freezing server is not supported")

    def unfreeze(self):
        """ Unfreezes the server """
        raise NotImplementedError("Unfreezing server is not supported")

    def kill(self):
        """ Kills the server """
        self.process.kill()
        self.process = None
        self.state = SERVER_STOPPED

    # Commands
    def run(self, cmd):
        """ Runs a command on the server """
        if not self.process:
            raise ServerStopped()

        self.process.write("%s\n" % cmd)

    # Players
    def list_players(self, online=True, everyone=False):
        """ Returns a list containing all players.
        Defaults to online-only. """
        players = []

        # Load offline players before we begin
        # TODO: This is a bit of a hack, and should be replaced with a more 
        # intelligent way of loading offline players when applicable
        for player_data_path in os.listdir("wrapper-data/players"):
            try:
                name, ext = player_data_path.rsplit(".", 1)
            except:
                continue

            if ext != "mpack":
                continue

            mcuuid = uuid.UUID(name)

            try:
                self.get_player(mcuuid=mcuuid)
            except PlayerNotFound:
                player = Player(
                    server=self.server,
                    mcuuid=mcuuid
                )

                self.players.append(player)
                print("Adding player %s" % player)

        # Filter players
        for player in self._players:

            if not everyone:
                # Future criteria filters should go here
                if online and not player.online:
                    continue
                elif online == False and player.online:
                    continue

            players.append(player)

        return players
    
    @property
    def players(self):
        online_players = []

        for player in self._players:
            if player.online:
                online_players.append(player)

        return online_players

    def get_player(self, username=None, mcuuid=None, ip_address=None, add_if_not_found=False):
        for player in self._players:
            if username:
                if username == player.username:
                    return player

            if mcuuid:
                if player.mcuuid == mcuuid:
                    return player

            if ip_address:
                if player.ip_address == ip_address:
                    return player
        
        if add_if_not_found:
            mcuuid = self.uuid_cache.get(username)
            
            player = Player(
                server=self.server, 
                username=username, 
                mcuuid=mcuuid
            )

            self._players.append(player)

            return player

        raise PlayerNotFound("Player by criteria %s/%s/%s not found" % (username, mcuuid, ip_address))

    def get_player_(self, mcuuid):
        for player in self.list_players(everyone=True):
            if str(player.mcuuid) == mcuuid:
                return player

    # Tick
    def tick(self):
        # Process server output
        # This is done first, to ensure the buffer is cleared before the
        # in the event that the server process is dead
        for std, line in self.process.read_console():
            # Parse line
            print(line)
            parsed_event = self.parser.parse_line(line)

            if parsed_event:
                self.handler.process(parsed_event)

            # Call event for line
            self.events.call("server.console.output", line=line, parsed_event=parsed_event)

        # Check if server died during start; assume a problem, and
        # stop auto-restarting, to prevent a CPU-hogging bootloop
        if self.state == SERVER_STARTING and not self.process.process:
            self.log.error("Server stopped unexpectedly while booting.")
            self.server.stop()

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
                self.api.stop()
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

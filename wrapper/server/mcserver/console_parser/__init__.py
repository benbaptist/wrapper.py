import re
import time

from uuid import UUID

from wrapper.server.player import Player
from wrapper.server.world import World
from wrapper.commons import *
from wrapper.exceptions import *

class ConsoleParser:
    def __init__(self, mcserver):
        self.mcserver = mcserver
        self.server = mcserver.server

    def parse(self, line):
        # Compatible with most recent versions of Minecraft server
        new_style = re.search("(\[[0-9:]*\]) \[([A-z #0-9]*)\/([A-z #]*)\](.*)", line)
        old_style = re.search("([0-9-: ]*) \[([A-Z]*)\] (.*)", line)
        ansi_escape_8bit = re.compile(
            '(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])'
        )
        clean_line = ansi_escape_8bit.sub('', line)
        paper_style = re.search("\[([0-9:]*) ([A-z]*)\]()(.*)", clean_line)

        # If regex did not match, continue to prevent issues
        try:
            if new_style:
                return self.new_style(new_style)
            elif old_style:
                return self.old_style(old_style)
            elif paper_style:
                return self.new_style(paper_style)
        except Exception as e:
            print(line)
            self.server.log.traceback("Fatal error while parsing line from server: %s" % line)
            raise e

    def new_style(self, r):
        log_time = r.group(1)
        server_thread = r.group(2)
        log_level = r.group(3)
        output = r.group(4)

        print(output)
        if "IMSOVERYSPECIALLOL" in output:
            self.log.error("IMSOVERYSPECIALLOL")

        # print(r)

        # Parse output
        if self.mcserver.state == SERVER_STARTING:
            # Check for low-level Java errors
            r = re.search("(Exception in thread \"main\" java.lang.UnsupportedClassVersionError: )(.*)", r.string)
            if r:
                self.server.log.error("Fatal Java error occured.")

            # Grab server version
            r = re.search(": Starting minecraft server version (.*)", output)
            if r:
                server_version = r.group(1)
                self.mcserver.server_version = server_version

                for release in PROTOCOL_VERSIONS:
                    if release["minecraftVersion"] == server_version:
                        self.mcserver.server_version_protocol = \
                            release["version"]

            # Grab server port
            r = re.search(": Starting Minecraft server on \*:([0-9]*)", output)
            if r:
                server_port = r.group(1)

            # Grab world name
            r = re.search(": Preparing level \"(.*)\"", output)
            if r:
                level_name = r.group(1)
                self.mcserver.world = World(r.group(1))

            if output == ": The server will make no attempt to authenticate usernames. Beware.":
                self.mcserver.online_mode = False

            # Server started
            if "Done" in output:
                self.mcserver.state = SERVER_STARTED

                self.mcserver.command("gamerule sendCommandFeedback false")
                self.mcserver.command("gamerule logAdminCommands true")

                self.mcserver.events.call("server.started")

        if self.mcserver.state == SERVER_STARTED:
            # UUID catcher
            if "User Authenticator" in server_thread:
                r = re.search(": UUID of player (.*) is (.*)", output)

                if r:
                    username, uuid_string = r.group(1), r.group(2)
                    mcuuid = UUID(hex=uuid_string)

                    self.mcserver.uuid_cache.add(username, mcuuid)

            # Gamerule capture
            r = re.search(
                ": Gamerule (.*) is currently set to: (true|false)",
                output
            )
            if r:
                gamerule = r.group(1)
                value = bool(r.group(2))

                self.mcserver.gamerules[gamerule] = value

                # Surpress
                return False

            r = re.search(
                ": Gamerule (.*) is now set to: (true|false)",
                output
            )
            if r:
                # Surpress
                return False

            # Server Reload
            r1 = re.search(
                ": \[(.*)\: Reloading!]",
                output
            )

            r2 = re.search(
                ": Reloading!",
                output
            )

            r3 = re.search(
                ": Reloading ResourceManager: Default",
                output
            )

            # Paper & Bukkit
            r4 = re.search(
                ": Reloading ResourceManager: Default, bukkit",
                output
            )

            if r1 or r2 or r3 or r4:
                if r1:
                    username = r1.group(1)
                    player = self.server.get_player(username=username)
                else:
                    player = None

                self.mcserver.events.call(
                    "server.reload",
                    player=player
                )

                return False

            # Player Command
            r = re.search(
                ": \[(.*): (.*)\]",
                output
            )
            if r:
                username = r.group(1)
                command_response = r.group(2)

                player = self.server.get_player(username=username)

                self.mcserver.events.call(
                    "server.player.command_response",
                    player=player,
                    command_response=command_response
                )

            # Player Position
            r = re.search(
                ": Teleported (.*) to (.*), (.*), (.*)",
                output
            )
            r2 = re.search(
                "\[(.*): Teleported (.*) to (.*), (.*), (.*)\]",
                output
            )

            if r and not r2:
                username = r.group(1)
                x, y, z = r.group(2), r.group(3), r.group(4)
                x, y, z = float(x), float(y), float(z)

                player = self.server.get_player(username=username)
                player.position = [x, y, z]
                player.db["position_last_updated"] = time.time()

                self.mcserver.events.call(
                    "server.player.position",
                    player=player,
                    x=x,
                    y=y,
                    z=z
                )

                return False

            # Player Join
            r = re.search(": (.*)\[\/(.*):(.*)\] logged in with entity id (.*) at \((.*), (.*), (.*)\)", output)
            if r:
                username = r.group(1)
                ip_address = r.group(2)
                entity_id = r.group(4)

                try:
                    position = [
                        float(r.group(5)),
                        float(r.group(6)),
                        float(r.group(7))
                    ]
                except:
                    position = None

                try:
                    player = self.server.get_player(username=username)
                except TypeError:
                    mcuuid = self.mcserver.uuid_cache.get(username)

                    player = Player(server=self.mcserver.server, username=username, mcuuid=mcuuid)

                    self.mcserver.players.append(player)

                player.online = True
                player.ip_address = ip_address

                if position:
                    player.position = position

                self.mcserver.events.call("server.player.join", player=player)

            # Player Part
            r = re.search(": ([A-z0-9_]) lost connection: (.*)", output)
            if r:
                username = r.group(1)
                server_disconnect_reason = r.group(2)

                player = self.server.get_player(username=username)

                if player:
                    player.online = False
                    self.mcserver.events.call("server.player.part", player=player)

            # Chat messages
            r = re.search(": <(.*)> (.*)", output)
            if r:
                username, message = r.group(1), r.group(2)

                player = self.server.get_player(username=username)
                self.mcserver.events.call(
                    "server.player.message",
                    player=player,
                    message=message
                )

            # Misc. surpressions
            r = re.search(
                ": Showing new (.*) for (.*)",
                output
            )
            if r:
                return False

    def old_style(self, r):
        log_time = r.group(1)
        log_level = r.group(2)
        output = r.group(3)

        if self.mcserver.state == SERVER_STARTING:
            # Grab server version
            r = re.search("Starting minecraft server version (.*)", output)
            if r:
                server_version = r.group(1)
                self.mcserver.server_version = server_version

                for release in PROTOCOL_VERSIONS:
                    if release["minecraftVersion"] == server_version:
                        self.mcserver.server_version_protocol = \
                            release["version"]

            # Grab server port
            r = re.search("Starting Minecraft server on \*:([0-9]*)", output)
            if r:
                server_port = r.group(1)

            # Grab world name
            r = re.search("Preparing level \"(.*)\"", output)
            if r:
                level_name = r.group(1)
                self.mcserver.world = World(r.group(1))

            if output == "The server will make no attempt to authenticate usernames. Beware.":
                self.mcserver.online_mode = False

            # Server started
            if "Done" in output:
                self.mcserver.state = SERVER_STARTED

                self.mcserver.events.call("server.started")

        if self.mcserver.state == SERVER_STARTED:
            # Player Command
            r = re.search(
                "\[(.*): (.*)\]",
                output
            )
            if r:
                username = r.group(1)
                command_response = r.group(2)

                player = self.server.get_player(username=username)

                self.mcserver.events.call(
                    "server.player.command_response",
                    player=player,
                    command_response=command_response
                )

            # Player Position
            r = re.search(
                "Teleported (.*) to (.*), (.*), (.*)",
                output
            )
            r2 = re.search(
                "\[(.*): Teleported (.*) to (.*), (.*), (.*)\]",
                output
            )

            if r and not r2:
                username = r.group(1)
                x, y, z = r.group(2), r.group(3), r.group(4)
                x, y, z = float(x), float(y), float(z)

                player = self.server.get_player(username=username)
                player.position = [x, y, z]
                player.db["position_last_updated"] = time.time()

                self.mcserver.events.call(
                    "server.player.position",
                    player=player,
                    x=x,
                    y=y,
                    z=z
                )

                return False

            # Player Join
            r = re.search("(.*) \[\/(.*):(.*)\] logged in with entity id (.*) at \((.*), (.*), (.*)\)", output)
            if r:
                username = r.group(1)
                ip_address = r.group(2)
                entity_id = r.group(4)
                position = [
                    float(r.group(5)),
                    float(r.group(6)),
                    float(r.group(7))
                ]

                try:
                    player = self.server.get_player(username=username)
                except TypeError:
                    try:
                        mcuuid = self.mcserver.uuid_cache.get(username)
                    except EOFError:
                        mcuuid = self.mcserver.uuid_cache.get_offline_uuid(username)

                    player = Player(server=self.mcserver.server, username=username, mcuuid=mcuuid)

                    self.mcserver.players.append(player)

                player.online = True
                player.ip_address = ip_address

                self.mcserver.events.call("server.player.join", player=player)

            # Player Part
            r = re.search("(.*) lost connection: (.*)", output)
            if r:
                username = r.group(1)
                server_disconnect_reason = r.group(2)

                player = self.server.get_player(username=username)

                if player:
                    player.online = False
                    self.mcserver.events.call("server.player.part", player=player)

            # Chat messages
            r = re.search("<(.*)> (.*)", output)
            if r:
                username, message = r.group(1), r.group(2)

                player = self.server.get_player(username=username)
                self.mcserver.events.call(
                    "server.player.message",
                    player=player,
                    message=message
                )

            # Misc. surpressions
            r = re.search(
                "Showing new (.*) for (.*)",
                output
            )

            if r:
                return False

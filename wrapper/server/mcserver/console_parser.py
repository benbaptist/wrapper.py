import re
import time

from uuid import UUID

from wrapper.server.player import Player
from wrapper.commons import *
from wrapper.exceptions import *

class ConsoleParser:
    def __init__(self, mcserver):
        self.mcserver = mcserver

    def parse(self, line):
        # Compatible with most recent versions of Minecraft server
        r = re.search("(\[[0-9:]*\]) \[([A-z #0-9]*)\/([A-z #]*)\](.*)", line)

        # If regex did not match, continue to prevent issues
        if r == None:
            return

        log_time = r.group(1)
        server_thread = r.group(2)
        log_level = r.group(3)
        output = r.group(4)

        # Parse output
        if self.mcserver.state == SERVER_STARTING:
            # Grab server version
            r = re.search(": Starting minecraft server version (.*)", output)
            if r:
                server_version = r.group(1)

            # Grab server port
            r = re.search(": Starting Minecraft server on \*:([0-9]*)", output)
            if r:
                server_port = r.group(1)

            # Grab world name
            r = re.search(": Preparing level \"(.*)\"", output)
            if r:
                self.mcserver.world = r.group(1)

            if output == ": The server will make no attempt to authenticate usernames. Beware.":
                self.mcserver.online_mode = False

            # Server started
            if "Done" in output:
                self.mcserver.state = SERVER_STARTED
                self.mcserver.command("gamerule sendCommandFeedback false")
                self.mcserver.command("gamerule logAdminCommands false")
                self.mcserver.events.call("server.started")

        if self.mcserver.state == SERVER_STARTED:
            # UUID catcher
            if "User Authenticator" in server_thread:
                r = re.search(": UUID of player (.*) is (.*)", output)

                if r:
                    username, uuid_string = r.group(1), r.group(2)
                    mcuuid = UUID(hex=uuid_string)

                    self.mcserver.uuid_cache.add(username, mcuuid)

            # Player Join
            r = re.search(": (.*)\[\/(.*):(.*)\] logged in with entity id (.*) at \((.*), (.*), (.*)\)", output)
            if r:
                username = r.group(1)
                ip_address = r.group(2)
                entity_id = r.group(4)
                position = [
                    float(r.group(5)),
                    float(r.group(6)),
                    float(r.group(7))
                ]

                mcuuid = self.mcserver.uuid_cache.get(username)

                player = Player(server=self.mcserver.server, username=username, mcuuid=mcuuid)

                self.mcserver.players.append(player)

                self.mcserver.dirty = True
                self.mcserver.events.call("server.player.join", player=player)

            # Player Part
            r = re.search(": (.*) lost connection: (.*)", output)
            if r:
                username = r.group(1)
                server_disconnect_reason = r.group(2)

                player = self.mcserver.get_player(username=username)
                if player:
                    self.mcserver.events.call("server.player.part", player=player)

                    # print("Removing %s from players" % player)
                    self.mcserver.players.remove(player)

            # Chat messages
            r = re.search(": <(.*)> (.*)", output)
            if r:
                username, message = r.group(1), r.group(2)

                player = self.mcserver.get_player(username=username)
                self.mcserver.events.call(
                    "server.player.message",
                    player=player,
                    message=message,
                    ts=time.time()
                )

                self.mcserver._chat_scrollback.append([player, message, time.time()])

                # Purge chat scrollback to 200 lines
                while len(self.mcserver._chat_scrollback) > 200:
                    del self.mcserver._chat_scrollback[0]

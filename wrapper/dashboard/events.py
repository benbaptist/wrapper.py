from flask import g
from flask_socketio import Namespace, send, emit, join_room, leave_room

from wrapper.commons import *
from wrapper.__version__ import __version__

import time

class Events(Namespace):
    def __init__(self, wrapper, socketio, auth):
        self.wrapper = wrapper
        self.socketio = socketio
        self.verify_token = auth.verify_token
        self.events = wrapper.events

        self._chat_scrollback = []
        self._log_scrollback = []

        # Server state
        @self.events.hook("server.starting")
        def server_starting():
            self.socketio.emit("server.starting", room="server")

        @self.events.hook("server.started")
        def server_started():
            self.socketio.emit("server.started", room="server")

            self._chat_scrollback.append({
                "type": "server_started",
                "time": time.time()
            })

        @self.events.hook("server.stopping")
        def server_stopping():
            self.socketio.emit("server.stopping", room="server")

        @self.events.hook("server.stopped")
        def server_stopped():
            self.socketio.emit("server.stopped", room="server")

            self._chat_scrollback.append({
                "type": "server_stopped",
                "time": time.time()
            })

        # Server console output
        @self.events.hook("server.console.output")
        def server_console_output(line):
            while len(self._log_scrollback) > 500:
                del self._log_scrollback[0]

            self._log_scrollback.append(line)

            self.socketio.emit(
                "server.console.output",
                line,
                room="server"
            )

        # Server status
        @self.events.hook("server.status.ram")
        def server_status_ram(usage):
            self.socketio.emit("server.status.ram", {"usage": usage}, room="server")

        @self.events.hook("server.status.cpu")
        def server_status_cpu(usage):
            self.socketio.emit("server.status.cpu", {"usage": usage}, room="server")

        # Players
        @self.events.hook("server.player.join")
        def server_player_join(player):
            self.socketio.emit(
                "server.player.join",
                {
                    "player": player.__serialize__()
                },
                room="chat"
            )

            self._chat_scrollback.append({
                "player": player.__serialize__(),
                "type": "join",
                "time": time.time()
            })

        @self.events.hook("server.player.message")
        def server_player_message(player, message):
            self._chat_scrollback.append({
                "player": player.__serialize__(),
                "type": "message",
                "message": message,
                "time": time.time()
            })

            self.socketio.emit(
                "server.player.message",
                {
                    "player": player.__serialize__(),
                    "message": message
                },
                room="chat"
            )

        @self.events.hook("server.player.part")
        def server_player_part(player):
            self.socketio.emit(
                "server.player.part",
                {
                    "player": player.__serialize__()
                },
                room="chat"
            )

            self._chat_scrollback.append({
                "player": player.__serialize__(),
                "type": "part",
                "time": time.time()
            })

        # Backups
        @self.events.hook("backups.start")
        def backups_start():
            self.socketio.emit("backups.start", True)

        @self.events.hook("backups.complete")
        def backups_complete(details=None):
            self.socketio.emit("backups.complete", True)

            self.socketio.emit("backups.list", self.wrapper.backups.list())

        super(Events, self).__init__()

    def on_connect(self):
        join_room("server")

        if self.wrapper.backups.current_backup:
            emit("backups.start", True)
        else:
            emit("backups.complete", True)

        emit("backups.list", self.wrapper.backups.list())

    def on_server(self):
        self.verify_token()

        server = self.wrapper.server
        players = []

        if self.wrapper.server.mcserver:
            for player in server.players:
                players.append(
                    player.__serialize__()
                )

        if server.state == SERVER_STARTED:
            world = {
                "name": str(server.world),
                "size": server.world.size
            }
        else:
            world = None

        emit("server", {
            "state": server.state,
            "players": players,
            "world": world,
            "mcversion": server.version,
            "free_disk_space": None,
            "log": self._log_scrollback,
            "wrapperversion": __version__
        })

    def on_chat(self):
        self.verify_token()

        join_room("chat")

        emit("chat", self._chat_scrollback)

    def on_send_chat(self, message):
        self.verify_token()

        self.events.call(
            "server.player.message",
            player=self.wrapper.server._console_player,
            message=message
        )

        self.wrapper.server._console_player.message_as_player(message)

    def on_server_start(self):
        self.verify_token()

        self.wrapper.server.start()

    def on_server_restart(self):
        self.verify_token()

        self.wrapper.server.restart()

    def on_server_stop(self):
        self.verify_token()

        self.wrapper.server.stop()

    def on_set(self, name, value):
        print("%s: %s" % (name, value))

        if name == "server/jar":
            jar_path = self.wrapper.mojang.servers.get_jar_path(value)
            self.wrapper.config["server"]["jar"] = jar_path

        if name == "server/java-arguments":
            self.wrapper.config["server"]["arguments"] = value

        if name == "server/java-xms":
            self.wrapper.config["server"]["xms"] = int(value)

        if name == "server/java-xmx":
            self.wrapper.config["server"]["xmx"] = int(value)

        if name == "server/cmd":
            if len(value.strip()) == 0:
                self.wrapper.config["server"]["cmd"] = None
            else:
                self.wrapper.config["server"]["cmd"] = value

        if name == "server/auto-restart":
            self.wrapper.config["server"]["auto-restart"] = bool(value)

        # Backups
        if name == "backups/enable-backups":
            self.wrapper.config["backups"]["enable"] = bool(value)

        if name == "backups/backup-mode":
            self.wrapper.config["backups"]["backup-mode"] = value

        if name == "backups/include":
            self.wrapper.config["backups"]["enable-backups"] = bool(value)

        if name == "backups/destination":
            self.wrapper.config["backups"]["destination"] = value

        if name == "backups/interval-seconds":
            self.wrapper.config["backups"]["interval-seconds"] = int(value)

        if name == "backups/history":
            self.wrapper.config["backups"]["history"] = int(value)

        if name == "backups/only-backup-if-player-joins":
            self.wrapper.config["backups"]["only-backup-if-player-joins"] = bool(value)

        self.wrapper.config.save()

    # Backups
    def on_start_backup(self):
        try:
            self.wrapper.backups.start()
        except:
            return

    def on_delete_backup(self, id):
        self.wrapper.backups.delete(id)

        emit("backups.list", self.wrapper.backups.list())

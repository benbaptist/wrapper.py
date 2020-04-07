from flask import g
from flask_socketio import Namespace, send, emit, join_room, leave_room

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

        @self.events.hook("server.stopping")
        def server_stopping():
            self.socketio.emit("server.stopping", room="server")

        @self.events.hook("server.stopped")
        def server_stopped():
            self.socketio.emit("server.stopped", room="server")

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

        # Players #
        @self.events.hook("server.player.join")
        def server_player_join(player):
            self.socketio.emit(
                "server.player.join",
                {
                    "player": player.__serialize__()
                },
                room="chat"
            )

        @self.events.hook("server.player.message")
        def server_player_message(player, message):
            self._chat_scrollback.append({
                "player": player.__serialize__(),
                "message": message
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

        super(Events, self).__init__()

    def on_server(self):
        self.verify_token()

        join_room("server")

        server = self.wrapper.server
        players = []

        for player in server.players:
            players.append(
                player.__serialize__()
            )

        emit("server", {
            "state": server.state,
            "players": players,
            "world": {
                "name": None,
                "size": None
            },
            "mcversion": None,
            "free_disk_space": None,
            "log": self._log_scrollback
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

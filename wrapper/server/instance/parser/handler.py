from . import ParsedEvent
from ....commons import SERVER_STARTED, SERVER_STOPPED, SERVER_ERROR, SERVER_FROZEN, SERVER_RESTART, SERVER_STARTING, SERVER_STOPPING

class Handler:
    def __init__(self, instance):
        self.instance = instance

    def process(self, event: ParsedEvent):
        # TODO: this is a mess, and should be refactored
        if event.name == "player.message":
            self.handle_player_message(event)
        elif event.name == "player.join":
            self.handle_player_join(event)
        elif event.name == "server.start":
            self.handle_server_start(event)
        elif event.name == "server.port":
            self.handle_server_port(event)
        elif event.name == "server.world.prepare":
            self.handle_world_prepare(event)
        elif event.name == "server.ready":
            self.handle_server_ready(event)
        elif event.name == "player.disconnect":
            self.handle_player_disconnect(event)
        elif event.name == "player.teleport":
            self.handle_player_teleport(event)
        elif event.name == "server.auth.offline":
            self.handle_server_offline_mode(event)
        else:
            self.handle_unknown_event(event)

    def handle_player_message(self, event: ParsedEvent):
        player = self.instance.server.get_player(username=event.data["player"])

        if not player:
            return

        self.instance.events.call(
            "server.player.message", 
            player=player, 
            message=event.data["message"]
        )

    def handle_player_join(self, event: ParsedEvent):
        raw_player = event.data["player"]
        player = self.instance.server.get_player(username=raw_player["username"], add_if_not_found=True)

        if not player:
            return
        
        # TODO: Populate player object

        self.instance.events.call(
            "server.player.join", 
            player=player
        )

    def handle_server_start(self, event: ParsedEvent):
        self.instance.events.call(
            "server.start", 
            version=event.data["version"]
        )

    def handle_server_port(self, event: ParsedEvent):
        self.instance.events.call(
            "server.port", 
            port=event.data["port"]
        )

    def handle_world_prepare(self, event: ParsedEvent):
        self.instance.events.call(
            "server.world.prepare", 
            world=event.data["world"]
        )

    def handle_server_ready(self, event: ParsedEvent):
        self.instance.events.call(
            "server.ready"
        )
        self.instance.state = SERVER_STARTED

    def handle_player_disconnect(self, event: ParsedEvent):
        player = self.instance.server.get_player(username=event.data["player"])

        if not player:
            return

        self.instance.events.call(
            "server.player.disconnect", 
            player=player
        )

    def handle_player_teleport(self, event: ParsedEvent):
        player = self.instance.server.get_player(username=event.data["player"])

        if not player:
            return

        self.instance.events.call(
            "server.player.teleport", 
            player=player
        )

    def handle_server_offline_mode(self, event: ParsedEvent):
        self.instance.events.call(
            "server.auth.offline", 
            mode=event.data["mode"]
        )

    def handle_unknown_event(self, event: ParsedEvent):
        self.instance.events.call(
            "server.unknown", 
            raw_event=event
        )

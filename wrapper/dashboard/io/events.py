import time
from flask_socketio import emit
from ..auth import require_auth
from .. import socketio, app

@socketio.on('connect')
@require_auth
def handle_connect():
    """Handle client connection."""
    emit('server', get_server_status())

def get_server_status():
    """Get current server status."""
    instance = app.wrapper.server.instance
    if not instance:
        return {
            "status": "stopped",
            "version": None,
            "cpu_usage": 0,
            "memory_usage": 0,
            "players": []
        }

    return {
        "status": instance.state,
        "version": instance.server_version,
        "cpu_usage": instance.cpu_usage if hasattr(instance, 'cpu_usage') else 0,
        "memory_usage": instance.ram_usage if hasattr(instance, 'ram_usage') else 0,
        "players": [player.__serialize__() for player in instance.players]
    }

def init_events(wrapper):
    """Initialize event hooks. Called after wrapper is attached to app."""
    
    # Server events
    @wrapper.events.hook("server.start")
    def on_server_start(version):
        """Emit when server starts."""
        socketio.emit('server', get_server_status())

    @wrapper.events.hook("server.ready")
    def on_server_ready():
        """Emit when server is ready."""
        socketio.emit('server', get_server_status())

    @wrapper.events.hook("server.stopped")
    def on_server_stop():
        """Emit when server stops."""
        socketio.emit('server', get_server_status())

    @wrapper.events.hook("server.status.ram")
    def on_ram_update(usage):
        """Emit when RAM usage changes."""
        socketio.emit('server', get_server_status())

    @wrapper.events.hook("server.status.cpu")
    def on_cpu_update(usage):
        """Emit when CPU usage changes."""
        socketio.emit('server', get_server_status())

    # Player events
    @wrapper.events.hook("server.player.join")
    def on_player_join(player):
        """Emit when a player joins."""
        socketio.emit('server', get_server_status())

    @wrapper.events.hook("server.player.part")
    def on_player_part(player):
        """Emit when a player leaves."""
        socketio.emit('server', get_server_status())

    @wrapper.events.hook("server.player.message")
    def on_player_message(player, message):
        """Emit when a player sends a message."""
        socketio.emit('chat', {
            "player": player.__serialize__(),
            "message": message,
            "timestamp": int(time.time())
        })

    # Console output
    @wrapper.events.hook("server.console.output")
    def on_console_output(line, parsed_event):
        """Emit when there's console output."""
        pass
        # socketio.emit('logs', {
        #     "line": line,
        #     "parsed": parsed_event._asdict() if parsed_event else None,
        #     "timestamp": int(time.time())
        # }) 
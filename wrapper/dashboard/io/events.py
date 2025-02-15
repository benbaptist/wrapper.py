import time
from flask_socketio import emit, disconnect
from flask_login import current_user
from ..auth import check_auth_header
from .. import socketio, app

def authenticated_only(f):
    """Decorator that checks both session and API key auth for SocketIO."""
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated and not check_auth_header():
            disconnect()
            return
        return f(*args, **kwargs)
    return wrapped

@socketio.on('connect')
@authenticated_only
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

    @wrapper.events.hook("server.player.chat")
    def on_player_message(player, message):
        """Emit when a player sends a message."""
        # This event is for raw chat messages from the server
        # We don't need to handle it since the chat system will create ChatMessage objects
        pass

    # Chat events - hook into the chat system's events
    @wrapper.events.hook("server.chat.message")
    def on_chat_message(message):
        """Emit when a chat message is sent through the chat system."""
        socketio.emit('chat', {
            "player": message.player.__serialize__(),
            "message": message.content,
            "timestamp": int(message.timestamp.timestamp()),
            "is_private": message.is_private,
            "recipient": message.recipient.__serialize__() if message.recipient else None
        })

    # Console output
    @wrapper.events.hook("server.console.output")
    def on_console_output(line, parsed_event):
        """Emit when there's console output."""
        socketio.emit('logs', {
            "line": line,
            "parsed": parsed_event._asdict() if parsed_event else None,
            "timestamp": int(time.time())
        }) 
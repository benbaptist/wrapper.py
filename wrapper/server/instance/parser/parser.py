from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import re

@dataclass
class LogEntry:
    """Base structure for a parsed log entry before event processing"""
    timestamp: datetime
    logging_level: str
    thread: str
    message: str
    raw: str

@dataclass
class ParsedEvent:
    """Final parsed event structure"""
    timestamp: datetime
    logging_level: str
    message: str
    name: str
    data: Dict[str, Any]

class BaseLayer:
    """Base class for all parsing layers"""
    def process(self, data: Any) -> Any:
        raise NotImplementedError("Each layer must implement process()")

class TimestampLayer(BaseLayer):
    """First layer: Extracts timestamp and logging metadata"""
    
    # Example: [12:34:56] [Server thread/INFO]:
    LOG_PATTERN = re.compile(r'^\[(\d{2}:\d{2}:\d{2})\] \[(.*?)/(.*?)\]: (.*)$')
    
    def process(self, line: str) -> Optional[LogEntry]:
        if not line:
            return None
            
        match = self.LOG_PATTERN.match(line)
        if not match:
            return None
            
        time_str, thread, level, message = match.groups()
        
        # Convert time string to datetime (using today's date)
        current_time = datetime.combine(datetime.today(), datetime.strptime(time_str, "%H:%M:%S").time())
        
        return LogEntry(
            timestamp=current_time,
            logging_level=level,
            thread=thread,
            message=message.strip(),
            raw=line
        )

class MessageLayer(BaseLayer):
    """Second layer: Breaks down the message into constituent parts"""
    
    # Common message patterns
    PLAYER_CHAT = re.compile(r'^(?:\[Not Secure\] )?<(\w+)> (.*)$')
    PLAYER_JOIN = re.compile(
        r'^(\w+)\[/([^:]+):(\d+)\] logged in with entity id (\d+) at \(([-\d.]+), ([-\d.]+), ([-\d.]+)\)$'
    )
    
    # New patterns for server events
    SERVER_START = re.compile(r'^Starting minecraft server version (.+)$')
    SERVER_PORT = re.compile(r'^Starting Minecraft server on \*:(\d+)$')
    WORLD_PREPARE = re.compile(r'^Preparing level "([^"]+)"$')
    SERVER_READY = re.compile(r'^Done \(([\d.]+)s\)! For help, type "help"$')
    PLAYER_DISCONNECT = re.compile(r'^(\w+) lost connection: (.+)$')
    PLAYER_TELEPORT = re.compile(r'^\[(\w+): Teleported (\w+) to (\w+)\]$')
    SERVER_OFFLINE_MODE = re.compile(r'^The server will make no attempt to authenticate usernames\. Beware\.$')
    
    def process(self, entry: LogEntry) -> Tuple[str, Dict[str, Any]]:
        """Returns a tuple of (message_type, extracted_data)"""
        
        # Try to match player chat
        chat_match = self.PLAYER_CHAT.match(entry.message)
        if chat_match:
            username, message = chat_match.groups()
            return "player_chat", {
                "player": username,
                "message": message,
                "secure": not entry.message.startswith("[Not Secure]")
            }
            
        # Try to match player join
        join_match = self.PLAYER_JOIN.match(entry.message)
        if join_match:
            username, ip, port, entity_id, x, y, z = join_match.groups()
            return "player_join", {
                "player": {
                    "username": username,
                    "ip_address": ip,
                    "port": int(port),
                    "entity_id": int(entity_id),
                    "position": (float(x), float(y), float(z))
                }
            }
            
        # Try to match server startup sequence
        start_match = self.SERVER_START.match(entry.message)
        if start_match:
            version = start_match.group(1)
            return "server_start", {"version": version}
            
        port_match = self.SERVER_PORT.match(entry.message)
        if port_match:
            port = int(port_match.group(1))
            return "server_port", {"port": port}
            
        world_match = self.WORLD_PREPARE.match(entry.message)
        if world_match:
            world_name = world_match.group(1)
            return "world_prepare", {"world": world_name}
            
        ready_match = self.SERVER_READY.match(entry.message)
        if ready_match:
            startup_time = float(ready_match.group(1))
            return "server_ready", {"startup_time": startup_time}
            
        # Try to match player disconnect
        disconnect_match = self.PLAYER_DISCONNECT.match(entry.message)
        if disconnect_match:
            username, reason = disconnect_match.groups()
            return "player_disconnect", {
                "player": username,
                "reason": reason
            }
            
        # Try to match teleport command
        teleport_match = self.PLAYER_TELEPORT.match(entry.message)
        if teleport_match:
            executor, player, target = teleport_match.groups()
            return "player_teleport", {
                "executor": executor,
                "player": player,
                "target": target
            }
            
        # Try to match offline mode warning
        offline_match = self.SERVER_OFFLINE_MODE.match(entry.message)
        if offline_match:
            return "server_offline_mode", {"enabled": True}
            
        # Default case - unknown message type
        return "unknown", {"raw_message": entry.message}

class EventLayer(BaseLayer):
    """Third layer: Converts parsed messages into standardized events"""
    
    EVENT_MAPPINGS = {
        "player_chat": "player.message",
        "player_join": "player.join",
        "server_start": "server.start",
        "server_port": "server.port",
        "world_prepare": "server.world.prepare",
        "server_ready": "server.ready",
        "player_disconnect": "player.disconnect",
        "player_teleport": "player.teleport",
        "server_offline_mode": "server.auth.offline",
    }
    
    def process(self, entry: LogEntry, message_data: Tuple[str, Dict[str, Any]]) -> ParsedEvent:
        message_type, data = message_data
        
        return ParsedEvent(
            timestamp=entry.timestamp,
            logging_level=entry.logging_level,
            message=entry.message,
            name=self.EVENT_MAPPINGS.get(message_type, "unknown"),
            data=data
        )

class LogParser:
    """Main parser class that coordinates the parsing layers"""
    
    def __init__(self):
        self.timestamp_layer = TimestampLayer()
        self.message_layer = MessageLayer()
        self.event_layer = EventLayer()
    
    def parse_line(self, line: str) -> Optional[ParsedEvent]:
        """Parse a single line of log output through all layers"""
        
        # Layer 1: Extract timestamp and metadata
        entry = self.timestamp_layer.process(line)
        if not entry:
            return None
            
        # Layer 2: Parse the message content
        message_data = self.message_layer.process(entry)
        
        # Layer 3: Convert to final event
        return self.event_layer.process(entry, message_data)

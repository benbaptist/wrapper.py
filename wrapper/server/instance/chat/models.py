from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid

from ..player import Player

@dataclass
class ChatMessage:
    """Represents a single chat message in the server."""
    id: str
    player: Player  # The player who sent the message
    content: str
    timestamp: datetime
    is_private: bool = False
    recipient: Optional[Player] = None  # The recipient player for private messages
    
    @classmethod
    def create(cls, player: Player, content: str, recipient: Optional[Player] = None) -> "ChatMessage":
        """Factory method to create a new chat message."""
        return cls(
            id=str(uuid.uuid4()),
            player=player,
            content=content,
            timestamp=datetime.now(),
            is_private=recipient is not None,
            recipient=recipient
        ) 
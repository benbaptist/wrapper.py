from collections import deque
from typing import Optional, Iterator, List
from ..api.types.message import Message
from ..player import Player
from .models import ChatMessage

class Chat:
    """Manages chat functionality for the server instance."""
    def __init__(self, instance):
        self.instance = instance
        self._history = deque(maxlen=1000)  # Store up to 1000 messages
        
        # Hook into player chat events
        @instance.events.hook("server.player.chat")
        def on_player_chat(player: Player, message: str, **kwargs):
            # Don't create a new message object if it's one we sent
            if message.startswith("[PM]") or message.startswith("[PM to"):
                return
                
            chat_message = ChatMessage.create(player, message)
            self._history.append(chat_message)
        
    def __iter__(self) -> Iterator[ChatMessage]:
        """Iterate over all messages in history."""
        return iter(self._history)
        
    def __getitem__(self, index) -> ChatMessage:
        """Get a message by index."""
        return self._history[index]
        
    def __len__(self) -> int:
        """Get the number of messages in history."""
        return len(self._history)
        
    def send_message(self, player: Player, content: str, recipient: Optional[Player] = None) -> ChatMessage:
        """Send a chat message. If recipient is specified, it's a private message."""
        message = ChatMessage.create(player, content, recipient)
        self._history.append(message)
        
        if recipient:
            # Private message handling
            msg = Message(
                text=f"[PM] {player.username}: {content}",
                color="light_purple"
            )
            self.instance.api.message(recipient.username, msg)
            
            # Confirm to sender
            confirm_msg = Message(
                text=f"[PM to {recipient.username}] {content}",
                color="light_purple"
            )
            self.instance.api.message(player.username, confirm_msg)
        else:
            # Public message
            msg = Message(text=f"{player.username}: {content}")
            self.instance.api.message("@a", msg)
            
        return message
    
    def broadcast(self, content: str) -> ChatMessage:
        """Broadcast a system message to all players."""
        system_player = self.instance.get_player(username="Server", add_if_not_found=True)
        msg = Message(text=content, color="yellow")
        self.instance.api.message("@a", msg)
        
        message = ChatMessage.create(system_player, content)
        self._history.append(message)
        return message
    
    def simulate_player_message(self, player: Player, content: str) -> ChatMessage:
        """Simulate a message from a player that all players will see."""
        return self.send_message(player, content)
    
    def get_private_messages(self, player: Player) -> List[ChatMessage]:
        """Get all private messages involving a specific player."""
        return [
            msg for msg in self._history 
            if msg.is_private and (msg.player == player or msg.recipient == player)
        ]
    
    def clear_history(self):
        """Clear the message history."""
        self._history.clear() 
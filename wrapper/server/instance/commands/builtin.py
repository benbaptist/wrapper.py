from wrapper.__version__ import __version__
from ..api.types import Message

class BuiltinCommands:
    def __init__(self, wrapper, server, commands):
        self.wrapper = wrapper
        self.server = server
        self.commands = commands

        @self.commands.register("wrapper", permission="wrapper")
        def _wrapper(player, *command_args):
            if len(command_args) < 1:
                player.message(Message(
                    text=f"Wrapper.py ({__version__})",
                    color="green",
                    click_event={
                        "action": "open_url",
                        "value": "https://github.com/benbaptist/wrapper.py"
                    },
                    hover_event={
                        "action": "show_text",
                        "value": [
                            {
                                "text": "Click to open Wrapper.py's GitHub page",
                                "color": "aqua",
                                "bold": True
                            }
                        ]
                    }
                ))

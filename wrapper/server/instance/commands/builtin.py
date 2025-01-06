from wrapper.__version__ import __version__

class BuiltinCommands:
    def __init__(self, wrapper, server, commands):
        self.wrapper = wrapper
        self.server = server
        self.commands = commands

        @self.commands.register("wrapper", permission="wrapper")
        def _wrapper(player, *command_args):
            if len(command_args) < 1:
                player.message({
                    "text": "Wrapper.py (%s)" % __version__,
                    "color": "green",
                    "clickEvent": {
                        "action": "open_url",
                        "value": "https://github.com/benbaptist/wrapper.py"
                    },
                    "hoverEvent": {
                        "action": "show_text",
                        "value": [
                            {
                                "text": "Click to open Wrapper.py's GitHub page",
                                "color": "aqua",
                                "bold": True
                            }
                        ]
                    }
                })

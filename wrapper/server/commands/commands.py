from ...commons import *
from .builtin import BuiltinCommands
from .command import Command

from threading import Thread

COMMAND_PREFIX = "."

class Commands:
    def __init__(self, server):
        self.server = server
        self.wrapper = server.wrapper
        self.events = server.events

        self.commands = []

        @self.events.hook("server.player.message")
        def player_message(player, message):
            if message[0] == self.server.wrapper.config["server"]["command-prefix"]:
                t = Thread(target=self._parse_command, args=(player, message))
                t.daemon = True
                t.start()

        BuiltinCommands(self.wrapper, self.server, self)

    def _parse_command(self, player, raw_message):
        raw_message = raw_message[1:]

        command_name = args(0, raw_message).lower()
        command_args = args_after(1, raw_message).split(" ")

        if len(command_args) == 1:
            if len(command_args[0]) == 0:
                command_args = []

        commands = [] + self.commands

        # Find commands registered to plugins here
        for plugin in self.wrapper.plugins.plugins:
            for command in plugin.commands:
                commands.append(command)

        # Process commands
        for command in commands:
            if command.name == command_name:
                try:
                    command.run(player, *command_args)
                except:
                    self.server.log.traceback(
                        "Failure while processing command '%s'"
                        % command_name
                    )

                    player.message({
                        "text":
                            "An error occured while processing this "
                            "command. Please try again later.",
                        "color": "red"
                    })

    def _register(self, name, callback, permission, domain):
        command = Command(name, callback, permission, domain=None)
        self.commands.append(command)

    def register(self, name, permission=None, domain=None):
        def wrap(callback):
            self._register(name, callback, permission, domain)

        return wrap
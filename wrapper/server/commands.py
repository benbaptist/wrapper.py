from wrapper.commons import *

COMMAND_PREFIX = "."

class Commands:
    def __init__(self, server):
        self.server = server
        self.events = server.events

        self.commands = []

        @self.events.hook("server.player.message")
        def player_message(player, message):
            if message[0] == COMMAND_PREFIX:
                self._parse_command(player, message)

    def _parse_command(self, player, raw_message):
        raw_message = raw_message[1:]

        command_name = args(0, raw_message)
        command_args = args_after(1, raw_message).split(" ")

        commands = [] + self.commands

        # Find commands registered to plugins here
        # ...

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

    def _register(self, name, func, permission, domain):
        command = Command(name, func, permission, domain=None)
        self.commands.append(command)

    def register(self, name, permission=None, domain=None):
        def wrap(func):
            self._register(name, func, permission, domain)

        return wrap

    def unregister_domain(self, domain):
        i = 0

        while i < len(self.commands):
            command = self.commands[i]

            if command.domain == domain:
                print("Unregister %s" % command)
                del self.commands[i]

            i += 1

class Command:
    def __init__(self, name, callback, permission, domain):
        self.name = name
        self.callback = callback
        self.permission = permission
        self.domain = domain

    def run(self, *command_args):
        # insert permissions handling code here
        self.callback(*command_args)

class Command:
    def __init__(self, name, callback, permission, domain=None):
        self.name = name
        self.callback = callback
        self.permission = permission
        self.domain = domain

    def run(self, player, *command_args):
        # insert permissions handling code here
        self.callback(player, *command_args)

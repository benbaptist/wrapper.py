NAME = "Essentials Clone"
VERSION = (0, 2)
ID = "com.benbaptist.wrapper.essentials_clone"
SUMMARY = "Essential commands for the essential people."
DESCRIPTION = """This is a poor replica of the popular Bukkit plugin
of the same name. All the basic commands and utilities you'll need forever
and ever. Yay."""
WEBSITE = "https://github.com/benbaptist/wrapper.py"

import time

class Main:
    def __init__(self, api, log):
        self.api = api
        self.log = log

    def __enable__(self):
        @self.api.events.hook("server.player.join")
        def player_join(player):
            player.message({
                "text": "Hey %s, welcome back!" % player.username,
                "color": "green",
                "bold": True
            })

        @self.api.minecraft.command("ping")
        def ping(player, *command_args):
            player.message({
                "text": "Pong!",
                "color": "green"
            })

        @self.api.minecraft.command("coords")
        def coords(player, *cargs):
            def args(i):
                try:
                    return cargs[i]
                except:
                    return
            def args_after(i):
                try:
                    return " ".join(cargs[i:])
                except:
                    return

            if "coords" not in self.api.storage:
                self.api.storage["coords"] = []

            if player.username not in self.api.storage["coords"]:
                self.api.storage["coords"][player.username] = {}

            subcmd = args(0)

            if subcmd == "add":
                name = args_after(1)

                if len(name) < 1:
                    player.message({
                        "text": "Usage: .coords add [name ...]",
                        "color": "red"
                    })
                else:
                    x, y, z = player.position
                    x, y, z = int(x), int(y), int(z)

                    self.api.storage["coords"][player.username][name] = \
                        [x, y, z]

                    player.message({
                        "text": "Added '%s' (%s, %s, %s) to your coords list!"
                            % (name, x, y, z),
                        "color": "green"
                    })

                    print(self.api.storage["coords"][player.username])
            elif subcmd == "list":
                for name in self.api.storage["coords"][player.username]:
                    x, y, z = self.api.storage["coords"][player.username][name]
                    player.message({
                        "text": "* %s: %s, %s, %s" % (name, x, y, z),
                        "color": "aqua"
                    })
            elif subcmd == "remove":
                return
            else:
                player.message({
                    "text": "Usage: .coords <add/list/remove>",
                    "color": "red"
                })

        @self.api.minecraft.command("ping")
        def ping(player, *command_args):
            player.message({
                "text": "Pong!",
                "color": "green"
            })

        @self.api.minecraft.command("getpos")
        def getpos(player, *command_args):

            print(command_args)

            if len(command_args) > 0:
                target = None
            else:
                target = player

            player.message({
                "text": target.username,
                "color": "yellow",
                "bold": True,
                "hoverEvent": {
                    "action": "show_text",
                    "value": str(target.mcuuid)
                },
                "extra": [
                    {
                        "text": "'s position: "
                    },
                    {
                        "text": str(target.position),
                        "bold": False
                    }
                ]
            })

NAME = "Essentials Clone"
VERSION = (0.1)
ID = "com.benbaptist.wrapper.essentials_clone"

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

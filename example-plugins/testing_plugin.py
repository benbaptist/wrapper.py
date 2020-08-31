NAME = "Test Plugin"
AUTHOR = "Ben Baptist"
ID = "com.benbaptist.plugins.test_plugin"
SUMMARY = "I love testing things."
DESCRIPTION = "I love testing things. Testing things tests the time."
WEBSITE = "https://benbaptist.com/"
VERSION = (1, 0)

class Main:
    def __init__(self, api, log):
        self.api = api
        self.log = log

    def __enable__(self):
        self.log.info("Look ma, enabling plugin!")

        @self.api.events.hook("server.starting")
        def server_starting():
            self.log.info("The server is starting now!")

        @self.api.events.hook("server.started")
        def server_started():
            self.log.info("The server is started now!")

        @self.api.events.hook("wrapper.tick")
        def tick():
            return
            # Weird experimental position polling thing. 
            # Doesn't really work with the latest Wrapper builds.
            # for player in self.api.server.players:
                # def callback(x, y, z):
                #     print(player.username, x, y, z)
                # player.poll_position(callback)

        @self.api.minecraft.command("test")
        def test_command(player, *command_args):
            self.log.info("Test command was invoked")

            # def callback(x, y, z):
            #     player.message("x: %s, y: %s, z: %s" % (x, y, z))

            player.message({
                "text": "Test command activated! Great job! %s" % ",".join(command_args),
                "color": "yellow"
            })

            # player.poll_position(callback)

        @self.api.minecraft.command("echo")
        def echo(player):
            return

        @self.api.minecraft.command("fail")
        def fail(player):
            self.log.error("Uh oh, I sense a traceback coming on.")

            do_something_that_causes_a_deliberate_crash()

    def __disable__(self):
        self.log.info("Look ma, disabling plugin!")

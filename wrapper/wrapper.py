import os
import time
import threading
import logging
import argparse

from storify import Storify

from .__version__ import __version__
from .config import Config
from .log_manager import LogManager
from .server import Server
from .console import Console
from .backups import Backups
from .events import Events
from .scripts import Scripts
from .plugins import Plugins
from .mojang import Mojang
from .wizard import Wizard
from .commons import *

from builtins import input

class Wrapper:
    def __init__(self):
        self.log_manager = LogManager()
        self.log = self.log_manager.get_logger("main")

        # Check if wrapper-data folder exists before continuing
        self._is_fresh_start = False
        if not os.path.exists("wrapper-data"):
            os.mkdir("wrapper-data")

        if not os.path.exists("wrapper-data/config.json"):
            self._is_fresh_start = True

        # Configuration manager
        self.config = Config(path="wrapper-data/config.json",
            template=CONFIG_TEMPLATE,
            log=self.log_manager.get_logger("config")
        )

        # Database manager
        self.storify = Storify(
            root="wrapper-data/db",
            log=self.log_manager.get_logger("storify")
        )
        self.db = self.storify.get_db("main")

        # Core functionality
        self.plugins = Plugins(self)
        self.mojang = Mojang(self)
        self.events = Events()
        self.server = Server(self)
        self.console = Console(self)
        self.backups = Backups(self)
        self.scripts = Scripts(self)
        self.wizard = Wizard(self)

        self.abort = False
        self.initiate_shutdown = False

    @property
    def debug(self):
        """ Returns True if debug-mode is enabled, otherwise False. """
        return self.config["general"]["debug-mode"]

    def start(self):
        """ Starts Wrapper.py. """

        # Parse CLI arguments
        parser = argparse.ArgumentParser(
            description="Wrapper.py",
        )

        parser.add_argument("--ignore-config-updates", "-i",
            help="Prevent Wrapper from halting when configuration file updates",
            action="store_true")

        args = parser.parse_args()

        # First-time wizard
        if self._is_fresh_start:
            self.wizard.run()

        # Alert user if config was changed from an update, and shutdown
        if not self._is_fresh_start:
            if self.config.updated_from_template and not args.ignore_config_updates:
                self.log.info(
                    "Configuration file has been updated with new entries. Open "
                    "wrapper-data/config.json, and make sure your settings are "
                    "good before running."
                )
                return

        # Set logging level if debug mode is enabled
        if self.debug:
            self.log_manager.level = logging.DEBUG

        self.log.info("Wrapper starting (%s)" % __version__)
        self.log.debug("Debug mode is on.")

        # Start console input thread
        t = threading.Thread(target=self.console.read_console)
        t.daemon = True
        t.start()

        # Load plugins
        self.plugins.load_plugins()

        self.run()

        self.cleanup()

        self.log.info("Wrapper has stopped")

    def shutdown(self):
        self.initiate_shutdown = True

    def cleanup(self):
        self.plugins.unload_plugins()
        self.server.stop(save=False)
        self.storify.flush()

    def run(self):
        while not self.abort:
            try:
                self.tick()
            except KeyboardInterrupt:
                self.log.info("Wrapper caught KeyboardInterrupt, shutting down")
                self.shutdown()
            except:
                self.shutdown()
                self.log.traceback("Fatal error, shutting down")
                self.server.features.stop()

                t = time.time()

                while self.server.mcserver.process.process:
                    if time.time() - t > 60:
                        self.log.error("Taking too long for server to shutdown, killing")
                        self.server.kill()
                        break

                    time.sleep(1)

                break

    def tick(self):
        if self.initiate_shutdown and self.server.state != SERVER_STOPPING:
            self.server.stop(save=False)

        if self.initiate_shutdown and self.server.state == SERVER_STOPPED:
            self.abort = True
            return

        self.server.tick()
        self.backups.tick()
        self.storify.tick()

        self.events.call("wrapper.tick")

        time.sleep(1 / 20.0) # 20 ticks per second

def main():
    wrapper = Wrapper()
    wrapper.start()

if __name__ == "__main__":
    main()
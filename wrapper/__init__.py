import os
import time
import threading
import logging

from wrapper.__version__ import __version__
from wrapper.config import Config
from wrapper.storify import Storify
from wrapper.log_manager import LogManager
from wrapper.server import Server
from wrapper.console import Console
from wrapper.backups import Backups
from wrapper.events import Events
from wrapper.scripts import Scripts
from wrapper.dashboard import Dashboard
from wrapper.plugins import Plugins
from wrapper.mojang import Mojang
from wrapper.commons import *

class Wrapper:
    def __init__(self):
        self.log_manager = LogManager()
        self.log = self.log_manager.get_logger("main")

        # Check if wrapper-data folder exists before continuing
        if not os.path.exists("wrapper-data"):
            os.mkdir("wrapper-data")

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
        self.db = self.storify.getDB("main")

        # Core functionality
        self.plugins = Plugins(self)
        self.mojang = Mojang(self)
        self.events = Events()
        self.server = Server(self)
        self.console = Console(self)
        self.backups = Backups(self)
        self.scripts = Scripts(self)
        self.dashboard = Dashboard(self)

        self.abort = False
        self.initiate_shutdown = False

    @property
    def debug(self):
        """ Returns True if debug-mode is enabled, otherwise False. """
        return self.config["general"]["debug-mode"]

    def start(self):
        """ Starts Wrapper.py. """

        # Alert user if config was changed from an update, and shutdown
        if self.config.updated_from_template:
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

        # Start dashboard thread
        if self.config["dashboard"]["enable"]:
            t = threading.Thread(target=self.dashboard.run)
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

import os
import time
import threading
import logging
import argparse
import sys

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

from builtins import input

class Wrapper:
    def __init__(self):
        self.log_manager = LogManager()
        self.log = self.log_manager.get_logger("main")

        # Check if wrapper-data folder exists before continuing
        self._is_fresh_start = False
        if not os.path.exists("wrapper-data"):
            self._is_fresh_start = True
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
            def ask_bool(msg):
                while True:
                    answer = input("%s (y/n): " % msg).lower()

                    if answer == "y":
                        return True
                    elif answer == "n":
                        return False
                    else:
                        print("Please type 'y' or 'n', and then hit enter.")

            def ask_int(msg, safe_range=None):
                if safe_range:
                    safe_min = safe_range[0]
                    safe_max = safe_range[1]

                while True:
                    if safe_range:
                        answer = input("%s (%s-%s): " % (msg, safe_min, safe_max))
                    else:
                        answer = input("%s (number): " % msg)

                    try:
                        answer = int(answer)

                        if safe_range:
                            if answer < safe_min or answer > safe_max:
                                print("Please enter a number between %s and %s,"
                                    "and then hit enter."
                                    % (safe_min, safe_max))
                                continue

                        return answer
                    except:
                        print("Please enter a number, and then hit enter.")

            def ask_str(msg, default=None, min_len=None):
                while True:
                    if default:
                        answer = input("%s (default: %s): " % (msg, default))
                    else:
                        answer = input("%s: " % msg)

                    if min_len != None:
                        if len(answer) < min_len:
                            print("Your answer must be at least %s characters." % min_len)

                    if len(answer) < 1:
                        if default:
                            return default
                        else:
                            print("Please enter your answer, and then hit enter.")
                            continue

                    return answer

            print("* Welcome to Wrapper.py!")
            print("* Before we begin, let's get a few things set up.")
            print("-" * 16)
            use_dash = ask_bool("Would you like to use the web-based dashboard?")

            if use_dash:
                port = ask_int("What port would you like the dashboard to be on?",
                    safe_range=(1, 65535))
                bind = ask_str("What IP would you like the dashboard to bind to?"
                    , default="0.0.0.0")

                password = ask_str("Please enter a strong password to use", min_len=8)

                self.config["dashboard"]["enable"] = True
                self.config["dashboard"]["bind"]["ip"] = bind
                self.config["dashboard"]["bind"]["port"] = port
                self.config["dashboard"]["root-password"] = password

                print("You're all set to use the dashboard.")
                print("You'll access it using this URL: http://%s:%s" % (bind, port))
                print("When prompted, the username is 'root', and the password is the one you provided.")

                print("-" * 16)
                print("Wrapper.py will now save changes and exit. You may "
                "continue setting up Wrapper through the dashboard.")

                self.config.save()

                sys.exit(0)

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
                self.server.kill()

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

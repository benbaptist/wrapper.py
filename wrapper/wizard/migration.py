import sys
import os
import json

def migration(self):
    if os.path.exists("wrapper.properties.json"):
        if self.ask_bool("Detected an old Wrapper.py config file. Would you "
                    "like to import your settings from this file?"):

            with open("wrapper.properties.json", "r") as f:
                raw = f.read()
                old_config = json.loads(raw)

            command = old_config["General"]["command"].split(" ")
            jar_name = None
            for i in command:
                if ".jar" in i:
                    jar_name = i

            self.config["server"]["jar"] = jar_name
            self.config["server"]["timed-reboot"]["enabled"] = \
                old_config["General"]["timed-reboot"]
            self.config["server"]["timed-reboot"]["interval-seconds"] = \
                old_config["General"]["timed-reboot-minutes"] * 60
            self.config["server"]["timed-reboot"]["warning-seconds"] = \
                old_config["General"]["timed-reboot-warning-minutes"] * 60
            self.config["server"]["auto-restart"] = \
                old_config["General"]["auto-restart"]

            self.config["dashboard"]["enable"] = \
                old_config["Web"]["web-enabled"]
            self.config["dashboard"]["bind"]["ip"] = \
                old_config["Web"]["web-bind"]
            self.config["dashboard"]["bind"]["port"] = \
                old_config["Web"]["web-port"]

            if self.config["dashboard"]["enable"]:
                password = self.ask_str("Please enter a strong dashboard "
                    "password to use", min_len=8)
                self.config["dashboard"]["root-password"] = password

            self.config["backups"]["enable"] = \
                old_config["Backups"]["enabled"]
            self.config["backups"]["destination"] = \
                old_config["Backups"]["backup-location"]
            self.config["backups"]["ingame-notification"]["enable"] = \
                old_config["Backups"]["backup-notification"]
            self.config["backups"]["history"] = \
                old_config["Backups"]["backups-keep"]
            self.config["backups"]["interval-seconds"] = \
                old_config["Backups"]["backup-interval"]
            self.config["backups"]["include-paths"] = \
                old_config["Backups"]["backup-folders"]
            self.config["backups"]["backup-mode"] = "manual"

            print("Successfully imported settings. Re-run Wrapper to "
                "get started.")

            self.config.save()

            sys.exit(0)

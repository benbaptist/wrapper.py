import json
import sys
import os

class Wizard:
    def __init__(self, wrapper):
        self.wrapper = wrapper
        self.log = wrapper.log
        self.config = wrapper.config
        self.mojang = wrapper.mojang

    def ask_bool(self, msg):
        while True:
            answer = input("%s (y/n): " % msg).lower()

            if answer == "y":
                return True
            elif answer == "n":
                return False
            else:
                print("Please type 'y' or 'n', and then hit enter.")

    def ask_int(self, msg, safe_range=None):
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

    def ask_str(self, msg, default=None, min_len=None):
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

    def run(self):
        print("* Welcome to Wrapper.py!")
        print("* Before we begin, let's get a few things set up.")
        print("* By continuing, you agree to Mojang's EULA.")
        print("-" * 16)

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

        use_dash = self.ask_bool("Would you like to use the browser-based dashboard?")

        if use_dash:
            port = self.ask_int("What port would you like the dashboard to be on?",
                safe_range=(1, 65535))
            bind = self.ask_str("What IP would you like the dashboard to bind to?"
                , default="0.0.0.0")

            password = self.ask_str("Please enter a strong password to use", min_len=8)

            self.config["dashboard"]["enable"] = True
            self.config["dashboard"]["bind"]["ip"] = bind
            self.config["dashboard"]["bind"]["port"] = port
            self.config["dashboard"]["root-password"] = password

            print("You're all set to use the dashboard.")
            print("You'll access it using this URL: http://%s:%s" % (bind, port))
            print("When prompted, the username is 'root', and the password "
            "is the one you provided.")

            print("-" * 16)
            print("Wrapper.py will now save changes and exit. You may "
            "continue setting up Wrapper through the dashboard.")

            self.config.save()

            sys.exit(0)
        else:
            # Find server jars
            server_jars = []
            for fn in os.listdir("."):
                try:
                    name, ext = fn.rsplit(".", 1)
                except:
                    name, ext = fn, None

                if ext == "jar":
                    server_jars.append(fn)

            download_jar = False

            if len(server_jars) > 0:
                print("Please pick a server jar to use from the list:")

                for i, jar in enumerate(server_jars):
                    print(" - #%s: %s" % (i, jar))

                print(" - #%s: Download a new jar..." % len(server_jars))

                jar_to_use = self.ask_int("Pick an option", safe_range=(0, len(server_jars)))

                if jar_to_use == len(server_jars):
                    download_jar = True
                else:
                    self.config["server"]["jar"] = server_jars[jar_to_use]

            else:
                if self.ask_bool("Wrapper.py could not detect any existing server"
                    "jars in this folder. Would you like to download one?"):
                    download_jar = True

            if download_jar:
                all_server_jars = self.mojang.servers.versions

                latest_snapshot = None
                latest_release = None

                for server_jar in all_server_jars:
                    print(server_jar["type"], server_jar["id"])
                    if server_jar["type"] == "snapshot":
                        latest_snapshot = server_jar
                        break

                for server_jar in all_server_jars:
                    if server_jar["type"] == "release":
                        latest_release = server_jar
                        break

                print("-" * 16)
                print("Pick a server jar to use:")

                print(" - #1: Latest release (%s)" % latest_release["id"])
                print(" - #2: Latest snapshot (%s)" % latest_snapshot["id"])
                print(" - #3: Cancel")

                option = self.ask_int("Select a download", safe_range=(1, 3))
                if option == 1:
                    print("Downloading the latest release...")
                    server_jar_path = self.mojang.servers.get_jar(
                        latest_release["id"]
                    )

                    self.config["server"]["jar"] = server_jar_path
                elif option == 2:
                    print("Downloading the latest snapshot...")
                    server_jar_path = self.mojang.servers.get_jar(
                        latest_snapshot["id"]
                    )

                    self.config["server"]["jar"] = server_jar_path

            print("You're all set. Wrapper.py will save and exit. Re-run it"
                "to get started with all your Wrappery wrappness.")

            self.config.save()

            sys.exit(0)

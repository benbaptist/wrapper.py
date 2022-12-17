import json
import os
import time
import pickle
import shutil

from wrapper.server.uuid_cache import UUID_Cache

class Player:
    def __init__(self, server, username=None, mcuuid=None, online_mode=None):
        self.server = server
        self.mojang = server.wrapper.mojang
        self.events = server.wrapper.events

        self.username = username
        self.mcuuid = mcuuid

        if not os.path.exists("wrapper-data/players"):
            os.makedirs("wrapper-data/players")

        self.db = self.server.wrapper.storify.get_mini_db(
            "wrapper-data/players/%s.mpack" % str(self.mcuuid)
        )

        self.db["online"] = False

        if not username:
            if "username" in self.db:
                self.username = self.db["username"]
        else:
            self.db["username"] = username

        if "current_login" not in self.db:
            self.db["current_login"] = None

        if "login_history" not in self.db:
            self.db["login_history"] = []

        if self.db["current_login"]:
            current_login = self.db["current_login"]

            self.db["login_history"].append({
                "logged_in": current_login["logged_in"],
                "logged_out": current_login["last_updated"],
                "ip_address": current_login["ip_address"]
            })

            self.db["current_login"] = None

        if "position_last_updated" not in self.db:
            self.db["position_last_updated"] = 0

        # Migrate old Wrapper.py 1.x pickled files
        old_path = os.path.join("wrapper-data/players", "%s.pkl" % str(self.mcuuid))
        if os.path.exists(old_path):
            self.server.log.info("MIGRATING %s" % old_path)

            fh = open(old_path, "rb")
            pkl = pickle.Unpickler(fh)
            data = pkl.load()

            if "logins" in data:

                for logged_in in data["logins"]:
                    logged_out = data["logins"][logged_in]
                    self.db["login_history"].append({
                        "logged_in": logged_in,
                        "logged_out": logged_out,
                        "ip_address": None
                    })

            if "firstLoggedIn" in data:

                self.first_login = data["firstLoggedIn"][0]

            # Prevent migration from happening twice
            shutil.move(old_path, old_path + ".MIGRATED")

        # Check online mode
        if online_mode in (False, True):
            self.online_mode = online_mode
        else:
            self.online_mode = self.server.online_mode

        if "is_online_accounat" not in self.db:
            self.db["is_online_account"] = True

            uuid_cache = UUID_Cache()

            if uuid_cache.get_offline_uuid(self.username) == mcuuid:
                self.db["is_online_account"] = False

        if not self.db["is_online_account"]:
            self.online_mode = False

        # Grab skin if applicable
        if self.online_mode:
            self.skin = self.mojang.get_skin_from_uuid(self.mcuuid)
        else:
            self.skin = None

        # Events
        @self.events.hook("server.player.join")
        def on_join(player):
            if player != self:
                return

            self.online = True

            self.db["last_login"] = time.time()
            self.db["current_login"] = {
                "logged_in": time.time(),
                "last_updated": time.time(),
                "ip_address": self.ip_address
            }

            if not self.first_login:
                self.first_login = time.time()

        @self.events.hook("wrapper.tick")
        def on_tick():
            if self.db["current_login"]:
                self.db["current_login"]["last_updated"] = time.time()

        @self.events.hook("server.player.part")
        def on_logout(player):
            if player != self:
                return

            self.db["login_history"].append({
                "logged_in": self.db["last_login"],
                "logged_out": time.time(),
                "ip_address": self.ip_address
            })

            self.db["current_login"] = None
            self.online = False

        @self.events.hook("server.player.chat")
        def on_chat(player, message):
            if player != self:
                return

            self.db["login_history"].append({
                "logged_in": self.db["last_login"],
                "logged_out": time.time(),
                "ip_address": self.ip_address
            })

            self.db["current_login"] = None
            self.online = False

    # Properties
    @property
    def position(self):
        if self.online:
            if time.time() - self.db["position_last_updated"] > 1:
                self.server.run("execute at %s run tp %s ~ ~ ~"
                    % (self.username, self.username)
                )

                poll_start = time.time()
                while time.time() - self.db["position_last_updated"] > 1:
                    if time.time() - poll_start > 1:
                        print("Timeout: player.position")
                        break

                    time.sleep(.01)
        else:
            # Read from NBT file
            pass

        try:
            return self.db["position"]
        except:
            return

    @position.setter
    def position(self, xyz):
        self.db["position"] = xyz

    @property
    def ip_address(self):
        if self.online:
            return self.db["ip_address"]

    @ip_address.setter
    def ip_address(self, ip_address):
        try:
            self.db["ip_address"] = ip_address
        except:
            return

    @property
    def entity_id(self):
        return self.db["entity_id"]

    @entity_id.setter
    def entity_id(self, entity_id):
        self.db["entity_id"] = entity_id

    @property
    def online(self):
        return self.db["online"]

    @online.setter
    def online(self, value):
        self.db["online"] = value

    @property
    def skin(self):
        try:
            return self.db["skin"]
        except:
            return

    @skin.setter
    def skin(self, url):
        self.db["skin"] = url

    @property
    def first_login(self):
        try:
            return self.db["first_login"]
        except:
            return

    @first_login.setter
    def first_login(self, ts):
        self.db["first_login"] = int(ts)

    @property
    def stats(self):
        total_playtime_seconds = 0
        last_time_seen = 0

        for login in self.db["login_history"]:
            logged_in = login["logged_in"]
            logged_out = login["logged_out"]

            total_playtime_seconds += logged_out - logged_in
            last_time_seen = logged_out

        # total_playtime_seconds += time.time() - self.db["current_login"]["logged_in"]

        return {
            "total_playtime_seconds": total_playtime_seconds,
            "last_time_seen": last_time_seen
        }

    def __serialize__(self):
        return {
            "username": self.username,
            "mcuuid": str(self.mcuuid),
            "ip_address": self.ip_address,
            "skin": self.skin,
            "online": self.online
        }

    @property
    def op(self):
        # This needs to be cached for performance
        if os.path.exists("ops.json"):
            with open("ops.json", "r") as f:
                ops = json.loads(f.read())

                for op in ops:
                    if op["uuid"] == str(self.mcuuid):
                        if op["level"] == 4:
                            return True

        return False

    # Methods

    def message(self, message):
        """ Sends a /tellraw message to this player. """
        self.server.features.message(self.username, message)

    def message_as_player(self, message):
        """ Simulates sending a message as this player. """
        self.server.log.info("<%s> %s" % (self.username, message))
        self.server.broadcast("<%s> %s" % (self.username, message))

    def kick(self, reason="Kicked from server"):
        self.server.run(
            "kick %s %s"
            % (self.username, reason)
        )

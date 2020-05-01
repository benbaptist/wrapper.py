import requests
import base64
import json
import time

class Mojang:
    def __init__(self, wrapper):
        self.wrapper = wrapper
        self.log = wrapper.log_manager.get_logger("mojang")

        self.db = wrapper.storify.getDB("mojang-api-cache")
        if "cache" not in self.db:
            self.db["cache"] = []

    def _get_cache(self, action, value):
        for obj in self.db["cache"]:
            if obj["action"] == action and obj["value"] == value:

                # If cache object is older than 24 hours, discard
                if time.time() - obj["time"] > 60 * 60 * 24:
                    self.log.debug("Discarding cache %s/%s" % (action, value))
                    self.db["cache"].remove(obj)
                    return

                return obj["payload"]

    def _write_cache(self, action, value, payload):
        self.db["cache"].append({
            "action": action,
            "value": value,
            "payload": payload,
            "time": time.time()
        })

    def uuid_to_profile(self, mcuuid):
        mcuuid = str(mcuuid)
        mcuuid = mcuuid.replace("-", "")

        cache = self._get_cache("uuid_to_profile", mcuuid)
        if cache:
            return cache

        r = requests.get(
            "https://sessionserver.mojang.com/session/minecraft/profile/%s"
            % mcuuid
        )

        try:
            payload = r.json()
        except:
            return

        assert payload["id"] == mcuuid

        self.log.debug("Fetch profile from UUID %s " % mcuuid)

        self._write_cache("uuid_to_profile", mcuuid, payload)

        return payload

    def get_skin_from_uuid(self, mcuuid):
        """ Fetches a skin object from the player UUID. """

        profile = self.uuid_to_profile(mcuuid)

        if not profile:
            return

        for prop in profile["properties"]:
            if prop["name"] == "textures":
                value_b64 = base64.b64decode(prop["value"])
                value_json = value_b64.decode("utf-8")
                value = json.loads(value_json)

                if "SKIN" in value["textures"]:
                    skin = value["textures"]["SKIN"]

                    self.log.debug("Returning skin for %s " % mcuuid)

                    return skin

        return None

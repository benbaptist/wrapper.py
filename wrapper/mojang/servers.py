import requests
import os

class Servers(object):
    def __init__(self, mojang):
        self.mojang = mojang

        if not os.path.exists("wrapper-data/jars"):
            os.mkdir("wrapper-data/jars")

    @property
    def _versions(self):
        cache = self.mojang._get_cache("minecraft_server", "versions")

        if cache:
            return cache

        r = requests.get(
            "https://launchermeta.mojang.com/mc/game/version_manifest.json"
        )

        try:
            payload = r.json()

            self.mojang._write_cache("minecraft_server", "versions", payload)
        except:
            return

        return payload

    @property
    def versions(self):
        versions = []

        for version in self._versions["versions"]:
            server_jar_name = "server.%s.jar" % version["id"]
            server_jar_path = self.get_jar_path(version["id"])

            if os.path.exists(server_jar_path):
                path = server_jar_path
            else:
                path = None

            _version = {
                "path": path,
                "type": version["type"],
                "id": version["id"],
                "releaseTime": version["releaseTime"],
                "url": version["url"]
            }

            versions.append(_version)

        return versions

    @property
    def latest_version(self):
        return self._versions["latest"]

    def get_jar_path(self, version):
        return "wrapper-data/jars/server.%s.jar" % version

    def get_jar(self, version):
        for ver in self.versions:
            if ver["id"] == version:
                server_jar_name = "server.%s.jar" % ver["id"]
                server_jar_path = self.get_jar_path(ver["id"])

                if os.path.exists(server_jar_path):
                    return os.path.realpath(server_jar_path)

                r = requests.get(ver["url"])
                payload = r.json()

                url_server_jar = payload["downloads"]["server"]["url"]

                r = requests.get(url_server_jar)

                with open(server_jar_path, "wb") as f:
                    f.write(r.content)

                return server_jar_path

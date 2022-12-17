import time
import os
import subprocess
import platform

from uuid import UUID

from wrapper.exceptions import *
from wrapper.commons import *
from wrapper.backups.backup import Backup

class Backups:
    def __init__(self, wrapper):
        self.wrapper = wrapper
        self.server = wrapper.server
        self.events = wrapper.events
        self.config = self.wrapper.config["backups"]
        self.log = wrapper.log_manager.get_logger("backups")
        self.backup_db = self.wrapper.storify.getDB("backups")

        if "backups" not in self.backup_db:
            self.backup_db["backups"] = []

        if "deleted_backups" not in self.backup_db:
            self.backup_db["deleted_backups"] = []

        # remove this non-sense after one commit
        for backup in self.backup_db["backups"]:
            if "id" not in backup:
                self.log.warning("assigning ID to backup %s" % backup)
                backup["id"] = str(UUID(bytes=os.urandom(16)))

        self.last_backup = time.time()
        self.current_backup = None
        self.dirty = False

    def start(self):
        """ Forces a backup to start, regardless of conditions. """
        if self.current_backup:
            raise Exception("Backup in progress")

        self.log.info("Starting backup")

        self.events.call("backups.start")

        self.current_backup = Backup(self)
        self.current_backup.start()

    def list(self):
        """ Returns a list of backups. """

        # Check for orphaned backups
        for backup in self.backup_db["backups"]:
            backup["orphan"] = False

            if not os.path.exists(backup["path"]):
                backup["orphan"] = True

        return self.backup_db["backups"]

    def get(self, id):
        for backup in self.backup_db["backups"]:
            if backup["id"] == id:
                return backup

        raise OSError("Backup not found in DB")

    def cancel(self):
        """ Cancels an ongoing backup, if applicable. """
        if not self.current_backup:
            raise EOFError("No ongoing backup")

        self.current_backup.cancel()

    def delete(self, id):
        """ Deletes a backup, both from the database and from the filesystem. """
        backup = self.get(id)

        path = backup["path"]
        if os.path.exists(path):
            os.remove(path)

        self.backup_db["deleted_backups"].append(backup)
        self.backup_db["backups"].remove(backup)

    def check_bin_installed(self, bin):
        which = "where" if platform.system() == "Windows" else "which"

        try:
            subprocess.check_output([which, bin])
        except subprocess.CalledProcessError:
            return False

        return True

    def get_best_archive_method(self):
        if self.check_bin_installed("7z"):
            return "7z"
        elif self.check_bin_installed("tar"):
            return "tar"
        elif self.check_bin_installed("zip"):
            return "zip"
        else:
            raise UnsupportedFormat(
                "No archival methods are installed. Please install either 7z, "
                "zip, or tar to use backups."
            )

    def get_archive_method(self):
        if self.config["archive-format"]["format"] == "auto":
            return self.get_best_archive_method()
        else:
            assert self.config["archive-format"]["format"] in ("tar", "7z", "zip")
            return self.config["archive-format"]["format"]

    def get_backup_destination(self):
        # Make this run through realpath later
        return self.config["destination"]

    def get_included_paths(self):
        if self.config["backup-mode"] == "auto":
            # Automatically determine folders and files
            # to backup, based off 'include' settings
            include = []

            if self.config["include"]["world"]:
                include.append(str(self.server.world))

            if self.config["include"]["logs"]:
                include.append("logs")

            if self.config["include"]["server-properties"]:
                include.append("server.properties")

            if self.config["include"]["wrapper-data"]:
                include.append("wrapper-data")

            if self.config["include"]["whitelist-ops-banned"]:
                include.append("banned-ips.json")
                include.append("banned-players.json")
                include.append("ops.json")
                include.append("whitelist.json")

            for include_path in self.config["include-paths"]:
                if include_path not in include:
                    include.append(include_path)

            return include
        elif self.config["backup-mode"] == "manual":
            # Only backup specified files in 'include-paths'
            return self.config["include-paths"]

    def tick(self):
        # If there's a current backup, check on it
        if self.current_backup:
            if self.current_backup.status == BACKUP_STARTED:
                self.server.title({
                    "text": "Backup started. Server may lag.",
                    "color": "red"
                }, title_type="actionbar")

            if self.current_backup.status == BACKUP_COMPLETE:
                details = self.current_backup.details

                if not details["filesize"]:
                    filesize = 0
                else:
                    filesize = details["filesize"]

                self.log.info(
                    "Backup complete. Took %s seconds, and uses %s of storage."
                    % (details["backup-complete"] - details["backup-start"],
                    bytes_to_human(filesize))
                )

            if self.current_backup.status == BACKUP_FAILED:
                details = self.current_backup.details

                if not details["filesize"]:
                    filesize = 0
                else:
                    filesize = details["filesize"]

                self.log.info(
                    "Backup complete, potentially with errors. Took %s seconds,"
                    " and uses %s of storage."
                    % (details["backup-complete"] - details["backup-start"],
                    bytes_to_human(filesize))
                )

            if self.current_backup.status in (BACKUP_COMPLETE, BACKUP_FAILED):
                details = self.current_backup.details

                self.server.title({
                    "text": "Backup complete.",
                    "color": "green"
                }, title_type="actionbar")

                self.dirty = False
                self.backup_db["backups"].append(self.current_backup.details)
                self.current_backup = None
                self.last_backup = time.time()

                self.events.call("backups.complete", details=details)

            return

        # If backups are disabled, skip tick
        if not self.config["enable"]:
            return

        # If server isn't fully started, skip tick
        if self.server.state != SERVER_STARTED:
            return

        # Mark server as dirty if needed
        if len(self.server.players) > 0:
            self.dirty = True

        # If server hasn't had a player join, skip tick
        if not self.dirty:
            if self.config["only-backup-if-player-joins"]:
                # This ensures backup counter STARTS once a player joins
                self.last_backup = time.time()
                return

        # Purge older backups
        while len(self.backup_db["backups"]) > self.config["history"]:
            backup = self.backup_db["backups"][0]

            self.log.info("Purging backup %s" % backup["name"])

            self.delete(backup["id"])

        # Check when backup is ready
        if time.time() - self.last_backup > self.config["interval-seconds"]:
            # If backup destination path doesn't exist or isn't set, skip backup
            destination = self.get_backup_destination()
            if not destination or not os.path.exists(destination):
                try:
                    os.makedirs(destination)
                except OSError:
                    self.log.error(
                        "Backup path could not be created. Skipping backup"
                    )

                self.last_backup = time.time()
                return

            self.start()

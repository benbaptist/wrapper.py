import time
import os

from subprocess import PIPE, Popen
from uuid import UUID
from threading import Thread

from wrapper.commons import *
from wrapper.exceptions import *

class Backup(object):
    def __init__(self, backups):
        self.backups = backups
        self.wrapper = backups.wrapper
        self.log = backups.log
        self.config = self.wrapper.config["backups"]

        self.name = None
        self.proc = None

        self.backup_complete = None

    @property
    def status(self):
        if not self.proc:
            return -1

        status_code = self.proc.poll()

        if status_code == 0:
            if not self.backup_complete:
                self.backup_complete = time.time()

            if not os.path.exists(self.path):
                if not self.backup_complete:
                    self.backup_complete = time.time()

                self.log.debug("BACKUP_FAILED / File does not exist")
                return BACKUP_FAILED

            self.log.debug("BACKUP_COMPLETE")

            return BACKUP_COMPLETE
        elif status_code == None:
            self.log.debug("BACKUP_STARTED")
            return BACKUP_STARTED
        else:
            if not self.backup_complete:
                self.backup_complete = time.time()

            self.log.debug("BACKUP_FAILED")
            return BACKUP_FAILED

        return BACKUP_STARTED

    @property
    def details(self):
        self.log.debug(".details called %s" % self.status)
        if not self.status in (BACKUP_COMPLETE, BACKUP_FAILED):
            raise EOFError("Backup is not complete")

        if os.path.exists(self.path):
            filesize = os.path.getsize(self.path)
        else:
            filesize = None

        return {
            "backup-start": self.backup_start,
            "backup-complete": self.backup_complete,
            "name": self.name,
            "path": self.path,
            "archive-method": self.archive_method,
            "filesize": filesize,
            "compression": self.config["archive-format"]["compression"]["enable"],
            "include-paths": self.backups.get_included_paths(),
            "id": str(UUID(bytes=os.urandom(16))),
            "orphan": False,
            "important": False
        }

    def build_command(self):
        include_paths = self.backups.get_included_paths()
        destination = self.backups.get_backup_destination()
        compression = self.config["archive-format"]["compression"]["enable"]

        self.archive_method = self.backups.get_archive_method()

        self.log.debug("Using archive method '%s'" % self.archive_method)

        path = os.path.join(destination, self.name)
        print("joined", path)

        if self.archive_method == "tar":
            path = "%s.%s" % (path, "tar.gz" if compression else "tar")

            command = [
                "tar", "-cvzf" if compression else "-cvf", path
            ] + include_paths
        elif self.archive_method == "7z":
            path = "%s.7z" % path

            command = [
                "7z", "a", "-mx=9" if compression else "-mx=0",
                path
            ] + include_paths
        elif self.archive_method == "zip":
            path = "%s.7z" % path

            command = [
                "zip", "-9" if compression else "-1",
                path
            ] + include_paths
        elif self.archive_method == "copy":
            print("mkdirs?")
            os.makedirs(path)
            print("hmmm")

            command = [
                "cp", "-rpv",
            ] + include_paths + [path, ]

            print(path, command)
        else:
            raise UnsupportedFormat(self.archive_method)

        print("returning thing", command, path)

        return (command, path)

    def execute_command(self, command):
        self.log.debug("Command: %s" % " ".join(command))
        self.proc = Popen(command, stdout=PIPE, stderr=PIPE)

        t = Thread(target=self.read_stdout, args=())
        t.daemon = True
        t.start()

        t = Thread(target=self.read_stderr, args=())
        t.daemon = True
        t.start()

    def start(self):
        self.backup_start = time.time()
        self.name = "backup_%s" % time.strftime("%Y-%m-%d_%H-%M-%S")

        command, self.path = self.build_command()
        self.execute_command(command)

    def read_stdout(self):
        """ an ugly hack that shouldn't really exist.
        I should be using shutil.copy anyways """

        while self.proc.stdout.read(1):
            continue

    def read_stderr(self):
        """ an ugly hack that shouldn't really exist.
        I should be using shutil.copy anyways """

        while self.proc.stdout.read(1):
            continue

    def cancel(self):
        raise Exception("Unimplemented feature")

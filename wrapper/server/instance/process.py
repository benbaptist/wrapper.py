import threading
import traceback
import resource
import psutil
import re

from subprocess import Popen, PIPE, check_output, STDOUT

from ...exceptions import *

class Process:
    def __init__(self):
        self.process = None
        self.process_status = None
        self.java_version = None
        self.threads = {}
        self.console_output = []

    def start(self, jar_name, java_args=[], java_bin="java",
            jar_args=["nogui"], command=None, java_xms=1024, java_xmx=2048):
        if self.process:
            raise StartingException("Cannot start java process, because it is \
                                    already running.")

        if not command:
            command = [java_bin] + java_args + ["-Xms%sM" % java_xms,
                "-Xmx%sM" % java_xmx] + ["-jar", jar_name] + jar_args

        self.process = Popen(
            command,
            stdout=PIPE,
            stderr=PIPE,
            stdin=PIPE,
            universal_newlines=True,
            bufsize=1)

        self.process_status = psutil.Process(self.process.pid)

        self.threads["__stdout__"] = threading.Thread(target=self.__stread__, args=("stdout", ))
        self.threads["__stdout__"].daemon = True
        self.threads["__stdout__"].start()

        self.threads["__stderr__"] = threading.Thread(target=self.__stread__, args=("stderr", ))
        self.threads["__stderr__"].daemon = True
        self.threads["__stderr__"].start()

        # Grab Java version
        output = check_output(["java", "-version"],
                                stderr=STDOUT)
        output = output.decode("utf8")

        for line in output.split("\n"):
            r = re.search("java version \"(.*)\"", line)

            if r:
                self.java_version = r.group(1)

    def get_ram_usage(self):
        with open("/proc/%d/statm" % self.process.pid) as f:
            getbytes = int(f.read().split(" ")[1]) * resource.getpagesize()

        return getbytes

    def get_cpu_usage(self):
        if not self.process_status and not self.process:
            return

        return self.process_status.cpu_percent()

    def read_console(self):
        i = 0
        while i < len(self.console_output):
            line = self.console_output[i]
            yield line

            del self.console_output[i]
            i += 1

    def kill(self):
        if self.process:
            self.process.kill()
            self.process = None
            self.process_status = None

    def write(self, cmd):
        if not self.process:
            raise ServerStopped("Can't write to server process because it is stopped")

        self.process.stdin.write(cmd)
        self.process.stdin.flush()

    def __stread__(self, read):
        try:
            assert read in ["stdout", "stderr"]

            if read == "stdout":
                std = self.process.stdout
            elif read == "stderr":
                std = self.process.stderr

            while self.process:
                blob = std.readline()

                if len(blob) < 1:
                    break

                for line in blob.split("\n"):
                    # Ignore empty lines
                    if len(line) < 1:
                        continue

                    # Strip line of \r
                    line = line.replace("\r", "")

                    self.console_output.append((read, line))

            # After loop is killed, ensure process is cleaned up
            self.kill()
        except:
            # If a fatal error occurs, print traceback and ensure process is cleaned up
            traceback.print_exc()
            self.kill()

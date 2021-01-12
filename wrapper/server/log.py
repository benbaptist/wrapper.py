import gzip
import os

class Log:
    def __init__(self, fn):
        self.fn = fn
        self.path = os.path.join("logs", fn)

        self._fh = None

    @property
    def fh(self):
        if not self._fh:
            name, ext = self.fn.rsplit(".", 1)

            if ext == "gz":
                self._fh = gzip.open(self.path, "r")
            else:
                self._fh = open(self.path, "r")

        return self._fh

    @property
    def filesize(self):
        return os.path.getsize(self.path)

    def readline(self, count):
        lines = []

        if count == -1:
            while True:
                line = self.fh.readline(1024).strip()

                if len(line) == 0:
                    break

                if type(line) == bytes:
                    line = line.decode("utf8")

                lines.append(line)
        else:
            for i in range(count):
                line = self.fh.readline(1024).strip()

                if type(line) == bytes:
                    line = line.decode("utf8")

                lines.append(line)

        return lines

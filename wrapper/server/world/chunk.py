import time

class Chunk:
    def __init__(self, world, x, z):
        self.world = world
        self.x = x
        self.z = z

        self._nbt = None
        self._nbt_last_updated = 0

    @property
    def nbt(self):
        # Update cache if older than a minute
        if time.time() - self._nbt_last_updated > 60:
            self._nbt = None

        if not self._nbt:
            self._nbt = self.world.get_nbt(self.x, self.z)

        return self._nbt

    @property
    def height(self):
        max_index = 0

        for section in self.nbt["Level"]["Sections"]:
            y = int(str(section["Y"]))

            if y > max_index:
                max_index = y

        return (max_index + 1) * 16

    @property
    def blocks(self):
        for section in self.nbt["Level"]["Sections"]:
            print(section)
            if "BlockStates" in section:
                return

import os

from nbt.world import WorldFolder

class World:
    def __init__(self, level_name):
        self.level_name = level_name

        self.world = WorldFolder(level_name)

        if self.world.type == "Anvil":
            # nbt.world.AnvilWorldFolder(level_name)
            for region in self.world.get_regionfiles():
                pass

    def __str__(self):
        return self.level_name

    @property
    def chunks(self):
        return self.world.get_chunks()

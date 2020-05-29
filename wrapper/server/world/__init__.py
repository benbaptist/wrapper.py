import os
import sys

from nbt.world import WorldFolder
from nbt.world import AnvilWorldFolder

from chunk import Chunk

class World:
    def __init__(self, level_name):
        self.level_name = level_name

        self.world = WorldFolder(level_name)

    def __str__(self):
        return self.level_name

    @property
    def chunks(self):
        # Currently incompatible with Python 3.x and above
        if sys.version_info.major > 2:
            raise Exception("This method currently only works with Python 2.x.")

        for basic_chunk in self.world.iter_chunks():
            print(basic_chunk)
            x, z = basic_chunk.get_coords()

            yield Chunk(self.world, x, z)

    @property
    def bounding_box(self):
        return self.world.get_boundingbox()

    @property
    def players(self):
        return

if __name__ == "__main__":
    print("Called directly for debugging purposes")
    # world = AnvilWorldFolder("world")

    # for chunk in world.chunks:
        # print(chunk)
    # help(world)

    world = World("world")
    # print(world.get_boundingbox())
    for chunk in world.chunks:
        for i in chunk.blocks:
            break
        break
    #     # help(chunk)
    #     max_height = chunk.get_max_height()
    #
    #     print(max_height, chunk)

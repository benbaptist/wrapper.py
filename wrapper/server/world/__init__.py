import os

from nbt.world import WorldFolder
from nbt.world import AnvilWorldFolder

from chunk import Chunk

class World:
    def __init__(self, level_name):
        self.level_name = level_name

        self.world = WorldFolder(level_name)

        if self.world.type == "Anvil":
            # nbt.world.AnvilWorldFolder(level_name)
            for region in self.world.get_regionfiles():
                # print(region)
                pass

    def __str__(self):
        return self.level_name

    @property
    def chunks(self):
        print(".chunks()")
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
    print("Called directly for debugging")
    # world = AnvilWorldFolder("world")

    # for chunk in world.chunks:
        # print(chunk)
    # help(world)

    world = World("world")
    # print(world.get_boundingbox())
    for chunk in world.chunks:
        for i in chunk.blocks:
            # print(i)
            pass
        break
    #     # help(chunk)
    #     max_height = chunk.get_max_height()
    #
    #     print(max_height, chunk)

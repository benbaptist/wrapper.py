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
        # Update cached version if older than a minute
        if time.time() - self._nbt_last_updated > 60:
            self._nbt = None

        if not self._nbt:
            self._nbt = self.world.get_nbt(self.x, self.z)
            print("self._nbt")

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
        # I wrote this while drunk. So, might be totally insane.
        blocks = [
            [
                [None] * 16
            ] * 16
        ] * 256

        for section in self.nbt["Level"]["Sections"]:
            y = int(str(section["Y"]))

            if "BlockStates" in section:
                blockstates = section["BlockStates"]
                palette = section["Palette"]

                _ = self._blockstates(blockstates)

                for index, block in enumerate(self._palette(_, palette)):
                    _y = y + (index / 256) - 1
                    z = (index - ((index / 256) * 256)) / 16
                    x = int(((index - ((index / 256) * 256)) / 16.0 % 1) * 16)

                    blocks[_y][z][x] = block

        return blocks

    def _palette(self, blocks, palette):
        _blocks = []
        for block in blocks:
            try:
                block_name = palette[block]["Name"]

                if block_name == "minecraft:air":
                    block_name = None

                _blocks.append(block_name)
            except IndexError:
                _blocks.append(None)

        return _blocks


    def _blockstates(self, blockstates):
        # Referenced from:
        # https://gist.github.com/Podshot/537e5e8f12fd580bdf1f705eb2b19119#file-proof_of_concept-py-L28

        return_value = [0] * 4096
        bit_per_index = len(blockstates) * 64 / 4096
        current_reference_index = 0

        for i in range(len(blockstates)):
            current = blockstates[i]

            overhang = (bit_per_index - (64 * i) % bit_per_index) % bit_per_index
            if overhang > 0:
                return_value[current_reference_index - 1] |= current % ((1 << overhang) << (bit_per_index - overhang))
            current >>= overhang

            remaining_bits = 64 - overhang
            for j in xrange((remaining_bits + (bit_per_index - remaining_bits % bit_per_index) % bit_per_index) / bit_per_index):
                return_value[current_reference_index] = current % (1 << bit_per_index)
                current_reference_index += 1
                current >>= bit_per_index

        return return_value

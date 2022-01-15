import numpy as np
from numpy.random import Generator, PCG64, SeedSequence


class BlockSampler2DBase:
    """
    Base class for samplers that provide fixed sized blocks.

    Overload `get_block` to create fixed-size data.

    The __call__ method allows getting a block of any size and position.
    """
    def __init__(self, block_size: int):
        self.block_size = block_size

    def get_block(self, block_x: int, block_y: int) -> np.ndarray:
        raise NotImplementedError

    def __call__(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        # first fixed block
        block_x0 = x // self.block_size
        block_y0 = y // self.block_size
        # end coords of required block
        x2 = x + width
        y2 = y + height
        # start coords of fixed block
        bx1 = block_x0 * self.block_size
        by1 = block_y0 * self.block_size
        # end coords of fixed block
        # bx2 = (x2 + self.block_size - 1) // self.block_size * self.block_size
        # by2 = (y2 + self.block_size - 1) // self.block_size * self.block_size

        rows = []
        for ly in range((y2 - by1 + self.block_size - 1) // self.block_size):
            row = []
            for lx in range((x2 - bx1 + self.block_size - 1) // self.block_size):
                row.append(self.get_block(block_x0 + lx, block_y0 + ly))

            rows.append(np.concatenate(row, axis=1))

        block = np.concatenate(rows, axis=0)

        #print(f"req {x} {y} {width} {height}")
        #print(f"blk {bx1} {by1} {block.shape[1]} {block.shape[0]}")
        if bx1 != x:
            assert bx1 < x, f"{bx1} {x}"
            block = block[:, x - bx1:]
        if block.shape[1] != width:
            assert width < block.shape[1], f"{width} {block.shape[1]}"
            block = block[:, :width - block.shape[1]]

        if by1 != y:
            assert by1 < y, f"{by1} {y}"
            block = block[y - by1:]
        if block.shape[0] != height:
            assert height < block.shape[0], f"{height} {block.shape[0]}"
            block = block[:height - block.shape[0]]

        return block


class RandomSampler2D(BlockSampler2DBase):

    def __init__(self, seed: int = 1, block_size: int = 32):
        super().__init__(block_size=block_size)
        self.seed = seed

    def get_block(self, block_x: int, block_y: int) -> np.ndarray:
        seed = abs(
                (self.seed * 2147483647)
                ^ (block_x * 391939)
                ^ (block_y * 2097593)
        )
        rnd = Generator(PCG64(seed))

        return rnd.random([self.block_size, self.block_size])

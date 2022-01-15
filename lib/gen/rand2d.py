import numpy as np
from numpy.random import Generator, PCG64, SeedSequence

from .sampler2d import BlockSampler2DBase
from .automaton import ClassicAutomaton


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


class AutomatonSampler2D(BlockSampler2DBase):

    def __init__(
            self,
            seed: int = 1,
            block_size: int = 32,
    ):
        super().__init__(block_size=block_size)
        self.random_sampler = RandomSampler2D(seed=seed, block_size=self.block_size)

    def get_block(self, block_x: int, block_y: int) -> np.ndarray:
        noise = self.random_sampler(
            (block_x - 1) * self.block_size,
            (block_y - 1) * self.block_size,
            self.block_size * 3, self.block_size * 3,
        )
        ca = ClassicAutomaton(
            self.block_size, self.block_size,
            born=(1, 2, 3),
            survive=(3, 4, 5, 6),
            cells=(noise + .5).astype("int32"),
        )
        ca.step(10)
        return ca.cells[self.block_size:-self.block_size, self.block_size:-self.block_size]
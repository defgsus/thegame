from typing import Iterable, Tuple

import numpy as np
from numpy.random import Generator, PCG64, SeedSequence

from .sampler2d import BlockSampler2DBase
from .automaton import ClassicAutomaton
from .perlin_noise import generate_perlin_noise_2d


class RandomSampler2D(BlockSampler2DBase):

    def __init__(self, seed: int = 1, block_size: int = 32):
        super().__init__(block_size=block_size)
        self.seed = seed

    def get_block(self, block_x: int, block_y: int) -> np.ndarray:
        rng = self.get_rng(self.seed, block_x, block_y)
        return rng.random([self.block_size, self.block_size])


class NoiseSampler2D(BlockSampler2DBase):

    def __init__(
            self,
            resolution: int = 1,
            seed: int = 1,
            block_size: int = 32,
    ):
        super().__init__(block_size=block_size)
        self.random_sampler = RandomSampler2D(seed, block_size=resolution)

    def get_block(self, block_x: int, block_y: int) -> np.ndarray:
        # need to get one block of initial data
        #   + the first column and row of the next blocks
        tl = self.random_sampler.get_block_cached(block_x, block_y)
        tr = self.random_sampler.get_block_cached(block_x+1, block_y)
        bl = self.random_sampler.get_block_cached(block_x, block_y+1)
        br = self.random_sampler.get_block_cached(block_x+1, block_y+1)
        noise = np.concatenate([
            np.concatenate([tl, tr], axis=1),
            np.concatenate([bl, br], axis=1),
        ])
        noise = noise[:self.random_sampler.block_size + 1, :self.random_sampler.block_size + 1]
        return generate_perlin_noise_2d(
            shape=(self.block_size, self.block_size),
            res=(self.random_sampler.block_size, self.random_sampler.block_size),
            values=noise,
        )


class AutomatonSampler2D(BlockSampler2DBase):

    def __init__(
            self,
            seed: int = 1,
            block_size: int = 32,
    ):
        super().__init__(block_size=block_size)
        self.random_sampler = RandomSampler2D(seed=seed, block_size=self.block_size)
        self._born = {3}
        self._survive = {2, 3}

    @property
    def born(self) -> set:
        return self._born

    @born.setter
    def born(self, value: Iterable[int]):
        self._born = value
        self.clear_cache()

    @property
    def survive(self) -> set:
        return self._survive

    @survive.setter
    def survive(self, value: Iterable[int]):
        self._survive = value
        self.clear_cache()

    def get_block(self, block_x: int, block_y: int) -> np.ndarray:
        noise = self.random_sampler(
            (block_x - 1) * self.block_size,
            (block_y - 1) * self.block_size,
            self.block_size * 3, self.block_size * 3,
        )
        ca = ClassicAutomaton(
            cells=(noise + .5).astype("int32"),
            born=self._born,
            survive=self._survive,
        )
        ca.step(10)
        return ca.total_neighbours()[self.block_size:-self.block_size, self.block_size:-self.block_size]

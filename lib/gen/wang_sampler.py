from typing import Iterable, Union

import numpy as np
from numpy.random import Generator, PCG64, SeedSequence

from .sampler2d import BlockSampler2DBase
from .rand2d import RandomSampler2D, AutomatonSampler2D
from .wang_tiling import WangTiling


class WangTilingSampler2D(BlockSampler2DBase):

    def __init__(
            self,
            probability: float = .3,
            seed: int = 1,
            block_size: int = 32,
            bottom_up: bool = True,
    ):
        super().__init__(block_size=block_size)
        self.probability = probability
        self.random_sampler = AutomatonSampler2D(seed=seed, block_size=self.block_size)
        # self.tile_mapping
        self.bottom_up = bottom_up

    def get_block(self, block_x: int, block_y: int) -> np.ndarray:
        padding = 1
        noise = self.random_sampler(
            block_x * self.block_size - padding,
            block_y * self.block_size - padding,
            self.block_size + padding * 2,
            self.block_size + padding * 2,
        )

        occupied = (noise > 3).astype("int32")
        tiling = WangTiling.get_edge_indices(occupied, bottom_up=self.bottom_up)
        if padding:
            tiling = tiling[padding:-padding, padding:-padding]
            occupied = occupied[padding:-padding, padding:-padding]

        return WangTiling.to_layout_indices(tiling, occupied_mask=occupied.astype("bool"))

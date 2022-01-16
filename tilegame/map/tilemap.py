import numpy as np

from lib.gen import *


class TilemapSampler(BlockSampler2DBase):

    def __init__(
            self,
            seed: int = 1,
            block_size: int = 32,
    ):
        super().__init__(block_size=block_size)
        self.biosphere_noise = NoiseSampler2D(
            resolution=2,
            seed=seed, block_size=128,
        )
        self.noise = NoiseSampler2D(
            resolution=8,
            seed=seed+23, block_size=128,
        )

        self.ca_sampler = AutomatonSampler2D(seed=seed, block_size=self.block_size)
        # self.random_sampler = RandomSampler2D(seed=seed, block_size=self.block_size)

    def __call__(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        padding = 1
        window = (
            x - padding,
            y - padding,
            width + padding * 2,
            height + padding * 2,
        )

        sea_land = self.biosphere_noise(*window)
        coast = 1. - np.abs(sea_land)

        noise1 = self.noise(*window)
        noise2 = self.ca_sampler(*window) / 4. - 1.

        level = (
            sea_land * .5 + .5
            + np.power(coast, 3) * noise1
            + np.power(coast, 7) * noise2 * .5
        )
        level = np.clip(level, 0, 1)

        # return (level[padding:-padding, padding:-padding] * 16).astype("int32")

        threshold = .5

        occupied = (level > threshold).astype("int32")
        tiling = WangTiling.get_edge_indices(occupied, bottom_up=True)

        if padding:
            tiling = tiling[padding:-padding, padding:-padding]
            occupied = occupied[padding:-padding, padding:-padding]
            level = level[padding:-padding, padding:-padding]

        wang_tiles = WangTiling.to_layout_indices(tiling, occupied_mask=occupied.astype("bool"))

        map = wang_tiles.reshape([height, width, 1]).repeat(3, axis=2)
        map[:, :, 1] = level * 10
        return map

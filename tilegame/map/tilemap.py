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
            resolution=16,
            seed=seed+23, block_size=128,
        )

        #self.ca_sampler = AutomatonSampler2D(seed=seed, block_size=self.block_size)
        self.random_sampler = RandomSampler2D(seed=seed, block_size=self.block_size)

    def get_block(self, block_x: int, block_y: int) -> np.ndarray:
        padding = 1
        window = (
            block_x * self.block_size - padding,
            block_y * self.block_size - padding,
            self.block_size + padding * 2,
            self.block_size + padding * 2,
        )

        sea_land = self.biosphere_noise(*window)
        coast = np.power(1. - np.abs(sea_land), 10)

        noise = self.noise(*window)

        level = (
            sea_land * .5 + .5
            + coast * noise
        )
        level = np.clip(level, 0, 1)

        # return (level[padding:-padding, padding:-padding] * 16).astype("int32")

        threshold = .5

        occupied = (level > threshold).astype("int32")
        tiling = WangTiling.get_edge_indices(occupied, bottom_up=True)
        if padding:
            tiling = tiling[padding:-padding, padding:-padding]
            occupied = occupied[padding:-padding, padding:-padding]

        return WangTiling.to_layout_indices(tiling, occupied_mask=occupied.astype("bool"))


class XXX_TileMap:

    BLOCK_SIZE = 32

    def __init__(self):
        self.random_sampler = NoiseSampler2D(seed=1, block_size=self.BLOCK_SIZE)
        self.ca_sampler = AutomatonSampler2D()

    def get_map(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        noise = self.random_sampler(x, y, width, height)
        return (noise * 20).astype("int32").astype("float32")

        return self.wang_sampler(x, y, width, height).astype("float32")
        #return wang_indices.astype("float32")
        #return WangTiling.to_layout_index(wang_indices).astype("float32")

        noise = self.random_sampler(x, y, width, height)
        map = (noise*3).astype("int32").astype("float32")

        # print(map)

        return map


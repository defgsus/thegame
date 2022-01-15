import numpy as np

from lib.gen import RandomSampler2D


class TileMap:

    BLOCK_SIZE = 32

    def __init__(self):
        self.random_sampler = RandomSampler2D(seed=1, block_size=self.BLOCK_SIZE)

    def get_map(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        noise = self.random_sampler(x, y, width, height)
        return (noise * 16).astype("int32").astype("float32")



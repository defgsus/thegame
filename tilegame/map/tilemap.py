import numpy as np

from lib.gen import *


class TileMap:

    BLOCK_SIZE = 32

    def __init__(self):
        #self.random_sampler = RandomSampler2D(seed=1, block_size=self.BLOCK_SIZE)
        self.random_sampler = AutomatonSampler2D()

    def get_map(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        noise = self.random_sampler(x, y, width, height)
        map = (noise*3).astype("int32").astype("float32")

        # print(map)

        return map


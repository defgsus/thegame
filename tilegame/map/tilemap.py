import numpy as np


class TileMap:

    def __init__(self):
        pass

    def get_map_block(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        return (np.random.random([height, width]) * 16).astype("int32").astype("float32")

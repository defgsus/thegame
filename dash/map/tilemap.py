from typing import Tuple, Optional

import numpy as np


class TileMap:

    def __init__(self, size: Tuple[int, int]):
        self.size = size
        self.map = np.zeros((size[1], size[0], 4), dtype="float32")
        self.state_id = 1

        self.map[:, :, 0] = np.random.uniform(0, 4, (size[1], size[0]))
        self.map[:, :, 1:] = np.random.uniform(0, 1, (size[1], size[0], 3))

    def set_dirty(self):
        """
        Call after changes to force re-rendering
        """
        self.state_id += 1

    def fill(self, x=0, y=0, z=0, w=0):
        self.map[:, :, :] = (x, y, z, w)
        self.set_dirty()

    def get_window(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        if y >= 0:
            window = self.map[y:y+height]
        else:
            window = np.concatenate([
                np.zeros((-y, *self.map.shape[1:]), dtype=self.map.dtype),
                self.map[:max(0, height + y)],
            ], axis=0)
        if window.shape[0] != height:
            window = np.concatenate([
                window,
                np.zeros((height - window.shape[0], *window.shape[1:]), dtype=self.map.dtype),
            ], axis=0)

        if x >= 0:
            window = window[:, x:x+width]
        else:
            window = np.concatenate([
                np.zeros((window.shape[0], -x, window.shape[2]), dtype=self.map.dtype),
                window[:, :max(0, width + x)],
            ], axis=1)
        if window.shape[1] != width:
            window = np.concatenate([
                window,
                np.zeros((window.shape[0], width - window.shape[1], window.shape[2]), dtype=self.map.dtype),
            ], axis=1)

        return window

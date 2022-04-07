from typing import Tuple, Optional

import numpy as np


class TileMap:

    def __init__(self, size: Tuple[int, int]):
        self.size = size
        self.map = np.zeros((size[1], size[0], 4), dtype="float32")
        self.state_id = 1
        self._outside = np.array([[[0, 0, 0, 0]]], dtype="float32")

    @property
    def width(self) -> int:
        return self.size[0]

    @property
    def height(self) -> int:
        return self.size[1]

    def set_dirty(self):
        """
        Call after changes to force re-rendering
        """
        self.state_id += 1

    def set_outside(self, x, y, z, w):
        self._outside[:] = (x, y, z, w)

    def fill(self, x=0, y=0, z=0, w=0):
        self.map[:, :, :] = (x, y, z, w)
        self.set_dirty()

    def random(self):
        self.fill()
        self.map[:, :, 0] = np.random.uniform(0, 10*6, (self.size[1], self.size[0]))
        #self.map[:, :, 1:] = np.random.uniform(0, .1, (size[1], size[0], 3))

    def get_window(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        if y >= 0:
            window = self.map[y:y+height]
        else:
            window = np.concatenate([
                self._outside_array(-y, self.map.shape[1]),
                self.map[:max(0, height + y)],
            ], axis=0)
        if window.shape[0] != height:
            window = np.concatenate([
                window,
                self._outside_array(height - window.shape[0], window.shape[1]),
            ], axis=0)

        if x >= 0:
            window = window[:, x:x+width]
        else:
            window = np.concatenate([
                self._outside_array(window.shape[0], -x),
                window[:, :max(0, width + x)],
            ], axis=1)
        if window.shape[1] != width:
            window = np.concatenate([
                window,
                self._outside_array(window.shape[0], width - window.shape[1]),
            ], axis=1)

        return window

    def _outside_array(self, height: int, width: int) -> np.ndarray:
        return self._outside.repeat(width, axis=1).repeat(height, axis=0)

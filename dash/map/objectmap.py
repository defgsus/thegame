from typing import Tuple, Optional, List

import numpy as np

from .tilemap import TileMap
from .object import Object

import pymunk


class ObjectMap:

    def __init__(self, static_map: TileMap):
        self.static_map = static_map
        self.objects: List[Object] = []
        self.state_id = 1
        self.space = pymunk.Space()

    def set_dirty(self):
        """
        Call after changes to force re-rendering
        """
        self.state_id += 1

    #def add_object(self, type: str, pos: Tuple[float, float]):
    #    self.objects.append(o)


    def get_window(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        window = np.zeros((height, width, 4))

        for i, o in enumerate(self.objects):
            int_x, int_y = o.int_pos
            if x <= int_x < x + width and y <= int_y < y + height:
                ox, oy = o.tile_offset
                tile_idx = 20 if i == 0 else 10
                window[int_y - y, int_x - x, :3] = (tile_idx, ox, oy)

        return window

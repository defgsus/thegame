from typing import Tuple

from .map import TileMap


class Object:
    def __init__(self, pos: Tuple[int, int]):
        self.pos = list(pos)


class World:

    def __init__(self):
        self.tile_map = TileMap((512, 512))
        self.player = Object((5, 2))

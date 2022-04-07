import math
from typing import Tuple

# from pymunk import Vec2d, Body, Shape, Circle, Segment, Poly


class Object:
    def __init__(self, pos: Tuple[float, float]):
        self.pos = list(pos)

    @property
    def int_pos(self) -> Tuple[int, int]:
        return int(self.pos[0]), int(self.pos[1])

    @property
    def tile_offset(self) -> Tuple[float, float]:
        return (
           self.pos[0] - math.floor(self.pos[0]),
           self.pos[1] - math.floor(self.pos[1]),
        )

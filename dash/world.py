import random
from typing import Tuple

from lib.gen.automaton import ClassicAutomaton
from .map import TileMap, Object, ObjectMap


class World:

    def __init__(self):
        self.tile_map = TileMap((512, 512))
        self.tile_map.set_outside(12, 0, 0, 0)
        #self.tile_map.random()
        self.init_map_gol(self.tile_map)
        self.object_map = ObjectMap(static_map=self.tile_map)
        self.object_map.objects = [
            Object((i, i))
            for i in range(30)
        ]

    @property
    def player(self) -> Object:
        return self.object_map.objects[0]

    def update(self, time: float, dt: float):
        for o in self.object_map.objects[1:]:
            if random.random() < dt:
                o.pos[0] += random.randint(-1, 1)
                o.pos[1] += random.randint(-1, 1)
                self.object_map.set_dirty()

    def init_map_gol(self, tile_map: TileMap):
        ca = ClassicAutomaton(
            tile_map.width, tile_map.height,
            born=(2, 3, 4, 5),
            survive=(2, 5,),
        )
        ca.init_random(.3, 23)
        ca.step(20)
        tile_map.map[:, :, 0] = 1 - ca.cells

import random
from typing import Tuple

from lib.gen.automaton import ClassicAutomaton
from .map import TileMap, Object, Objects


class World:

    def __init__(self):
        self.tile_map = TileMap((128, 128))
        self.tile_map.set_outside(12, 0, 0, 0)
        #self.tile_map.random()
        self.init_map_gol(self.tile_map)
        self.object_map = Objects(static_map=self.tile_map)

        pos_set = set()
        for i in range(1000):
            for j in range(1000):
                pos = random.randrange(min(self.width, i+10)), random.randrange(min(self.height, i+10))
                if pos not in pos_set:
                    pos_set.add(pos)
                    if not self.tile_map.map[pos[1], pos[0], 0]:
                        self.object_map.add_object(
                            shape_type="box" if i != 0 and random.random() < .2 else "circle",
                            pos=(pos[0] + .5, pos[1] + .5),
                        )
                        break

    @property
    def width(self) -> int:
        return self.tile_map.width

    @property
    def height(self) -> int:
        return self.tile_map.height

    @property
    def player(self) -> Object:
        return self.object_map.objects[0]

    def update(self, time: float, dt: float):
        if 0:
            for o in self.object_map.objects[1:]:
                if random.random() < dt:
                    o.body.position = (
                        o.body.position[0] + random.randint(-1, 1) * .1,
                        o.body.position[1] + random.randint(-1, 1) * .1,
                    )

        self.object_map.update(time, dt)

    def init_map_gol(self, tile_map: TileMap):
        ca = ClassicAutomaton(
            tile_map.width, tile_map.height,
            born=(2, 3, 4, 5),
            survive=(2, 5,),
        )
        ca.init_random(.3, 23)
        ca.step(20)
        tile_map.map[:, :, 0] = 1 - ca.cells

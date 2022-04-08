from typing import Tuple, Optional, List

import numpy as np
import pymunk

from .tilemap import TileMap
from .object import Object
from tests.util import Timer


class Objects:

    def __init__(self, static_map: TileMap):
        self.default_friction = 1.

        self.static_map = static_map
        self.objects: List[Object] = []
        self.space = pymunk.Space()
        self.space.gravity = (0, -10)
        self.static_objects = dict()
        self.last_static_map_state_id = None
        self._add_map_boundaries()

    @property
    def width(self) -> int:
        return self.static_map.width

    @property
    def height(self) -> int:
        return self.static_map.height

    def add_object(
            self,
            shape_type: str,
            pos: Tuple[float, float],
            scale: float = 1.,
    ) -> Object:
        o = Object(
            space=self.space,
            shape_type=shape_type,
            pos=pos,
            mass=1,
            scale=scale,
            friction=self.default_friction,
        )
        self.objects.append(o)
        if o.body != self.space.static_body:
            self.space.add(o.body)
        self.space.add(o.shape)
        return o

    def update(self, time: float, dt: float):
        if self.static_map.state_id != self.last_static_map_state_id:
            self.last_static_map_state_id = self.static_map.state_id
            self._update_static_map_objects()

        fixed_dt = 1./200.
        while dt > 0:
            self.space.step(fixed_dt)
            dt -= fixed_dt

    def dump_objects(self, file=None):
        for i, o in enumerate(self.objects):
            print(f"{i:3}: {o}", file=file)

    def _add_map_boundaries(self):
        for seg_start, seg_end in (
                ((-1, -1), (self.static_map.width, -1)),
                ((-1, self.static_map.height), (self.static_map.width, self.static_map.height)),
                ((-1, -1), (-1, self.static_map.height)),
                ((self.static_map.width, -1), (self.static_map.width, self.static_map.height)),
        ):
            shape = pymunk.Segment(self.space.static_body, seg_start, seg_end, 1)
            shape.friction = self.default_friction
            self.space.add(shape)

    def _update_static_map_objects(self):
        with Timer() as timer:
            shapes_to_add = []
            shapes_to_remove = []
            for pos, cell in self.static_map.iter_cells():
                shape_type = None
                if cell[0] > 0:
                    shape_type = "box"

                if not shape_type:
                    if pos in self.static_objects:
                        o = self.static_objects.pop(pos)
                        shapes_to_remove.append(o.shape)
                else:
                    if pos not in self.static_objects:
                        o = Object(
                            space=self.space,
                            shape_type=shape_type,
                            pos=(pos[0] + .5, pos[1] + .5),
                            mass=0,
                            friction=self.default_friction,
                        )
                        self.static_objects[pos] = o
                        shapes_to_add.append(o.shape)

        print("create shapes", timer)

        with Timer() as timer:
            for s in shapes_to_remove:
                self.space.remove(s)
            for s in shapes_to_add:
                self.space.add(s)

        print("add/remove shapes", timer)

    def dump_object_map(self):
        map = [[" "] * self.width for _ in range(self.height)]
        for pos, o in self.static_objects.items():
            x, y = int(o.position[0]), int(o.position[1])
            #x, y = pos
            if 0 <= x < self.width and 0 <= y < self.height:
                map[y][x] = "#"

        for o in self.objects:
            x, y = int(o.position[0]), int(o.position[1])
            if 0 <= x < self.width and 0 <= y < self.height:
                map[y][x] = "*"

        for row in reversed(map):
            print("".join(row))

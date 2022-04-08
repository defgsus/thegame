from typing import Tuple, Optional, List

import numpy as np

from .tilemap import TileMap
from .object import Object

import pymunk


class ObjectMap:

    def __init__(self, static_map: TileMap):
        self.default_friction = 0.1

        self.static_map = static_map
        self.objects: List[Object] = []
        self.state_id = 1
        self.space = pymunk.Space()
        self.space.gravity = (0, -10)
        self.static_objects = dict()
        self.last_static_map_state_id = None
        self._add_map_boundaries()

    def set_dirty(self):
        """
        Call after changes to force re-rendering
        """
        self.state_id += 1

    def add_object(self, type: str, pos: Tuple[float, float]) -> Object:
        o = Object(self.space, pos, mass=1, friction=self.default_friction)
        self.objects.append(o)
        self.space.add(o.body, o.shape)
        return o

    def update(self, time: float, dt: float):
        if self.static_map.state_id != self.last_static_map_state_id:
            self.last_static_map_state_id = self.static_map.state_id
            #self.space.

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
                ((-1, self.static_map.height), (self.static_map.width, -1)),
                ((-1, -1), (-1, self.static_map.height)),
                ((self.static_map.width, -1), (self.static_map.width, self.static_map.height)),
        ):
            shape = pymunk.Segment(self.space.static_body, seg_start, seg_end, 1)
            shape.friction = self.default_friction
            self.space.add(shape)

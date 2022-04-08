import math
from typing import Tuple

import pyglet
import pymunk

from .base import ControllerBase
from ..map import Object


class PlayerBugController(ControllerBase):

    def __init__(self, objects, pos: Tuple[float, float]):
        super().__init__()

        radius = .23
        small_radius = .1

        self.object = objects.add_object(
            shape_type="circle",
            pos=pos,
            mass=6.6,
            scale=radius*2.,
        )
        self.add_object(self.object)
        self.object.controller = self
        objects.add_controller(self)

        self.feet = []
        for i in range(6):
            r = i / 3 * math.pi

            anchor_pos = pymunk.Vec2d(
                (radius) * math.sin(r),
                (radius) * math.cos(r),
            )
            foot_pos = pymunk.Vec2d(
                pos[0] + (radius + small_radius) * math.sin(r),
                pos[1] + (radius + small_radius) * math.cos(r),
            )

            foot = objects.add_object(
                shape_type="circle",
                pos=foot_pos,
                scale=small_radius*2,
                mass=.1,
            )
            leg = pymunk.SlideJoint(
                self.object.body, foot.body,
                anchor_pos, (0, 0),
                min=0, max=small_radius,
            )
            self.space.add(leg)
            self.feet.append((foot, leg))

    def check_keys(self, keys: dict, dt: float):
        if keys.get(pyglet.window.key.LEFT):
            self.object.body.angular_velocity += dt*100.
        if keys.get(pyglet.window.key.RIGHT):
            self.object.body.angular_velocity -= dt*100.

        return
        dir_mapping = {
            pyglet.window.key.UP: (0, 1),
            pyglet.window.key.DOWN: (0, -1),
            pyglet.window.key.LEFT: (-1, 0),
            pyglet.window.key.RIGHT: (1, 0),
        }
        for key, delta in dir_mapping.items():
            if keys.get(key):
                self.object.apply_impulse(delta)

    def update(self, time: float, dt: float):
        pass

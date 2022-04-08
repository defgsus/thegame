import math
from typing import Tuple

import pymunk
from pymunk import Space, Vec2d, Body, Shape, Circle, Segment, Poly


SHAPE_TYPES = {
    "box": {},
    "circle": {},
}


class Object:

    def __init__(
            self,
            space: Space,
            shape_type: str,
            pos: Tuple[float, float],
            scale: float = 1.,
            mass: float = 0,
            friction: float = 0.1,
    ):
        points = [(-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5)]

        self.space = space
        self.shape_type = shape_type
        self._scale = scale

        if mass:
            if self.shape_type == "box":
                moment = pymunk.moment_for_box(mass, (self.scale, self.scale))
            elif self.shape_type == "circle":
                moment = pymunk.moment_for_circle(mass, 0, self.scale / 2.)
            else:
                raise ValueError(f"Invalid shape_type '{self.shape_type}'")

            self.mass = mass
            self.body = Body(mass, moment)
            self.body.position = pos
            self._static_position = None
            if self.shape_type == "box":
                self.shape = Poly.create_box(self.body, (1, 1))
            elif self.shape_type == "circle":
                self.shape = Circle(self.body, self.scale / 2.)
        else:
            self.mass = 0
            self.body = self.space.static_body
            self._static_position = Vec2d(*pos)

            if self.shape_type == "box":
                self.shape = Poly(self.space.static_body, [
                    (pos[0] + p[0] * scale, pos[1] + p[1] * scale)
                    for p in points
                ])
            elif self.shape_type == "circle":
                self.shape = Circle(self.space.static_body, self.scale / 2., offset=pos)

        self.shape.friction = friction

    @property
    def position(self) -> Vec2d:
        if self._static_position:
            return self._static_position
        return self.body.position

    @property
    def rotation(self) -> float:
        return self.body.angle

    @property
    def scale(self) -> float:
        return self._scale

    @property
    def texture_idx(self) -> int:
        return 13 if self.shape_type == "circle" else 10

    def __repr__(self):
        return f"Object({self.mass}, {self.position})"

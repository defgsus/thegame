import math
from typing import Tuple

import pymunk
from pymunk import Space, Vec2d, Body, Shape, Circle, Segment, Poly


class Object:
    def __init__(
            self,
            space: Space,
            pos: Tuple[float, float],
            mass: float = 0,
            friction: float = 0.1,
    ):
        points = [(-5., -.5), (.5, -.5), (.5, .5), (-.5, .5)]
        self.space = space
        if mass:
            self.mass = mass
            self.body = Body(mass, pymunk.moment_for_box(mass, (1, 1)))
            self.body.position = pos
            self.shape = Poly.create_box(self.body, (1, 1))
        else:
            self.mass = 0
            self.body = self.space.static_body
            self.shape = Poly(self.space.static_body, [
                (p[0] + pos[0], p[1] + pos[1])
                for p in points
            ])
        self.shape.friction = friction

    @property
    def position(self) -> Vec2d:
        return self.body.position

    @property
    def rotation(self) -> float:
        return self.body.angle

    @property
    def scale(self) -> float:
        return 1.

    def __repr__(self):
        return f"Object({self.mass}, {self.position})"

import math
from typing import Tuple, Optional

import glm
import pymunk
from pymunk import Space, Vec2d, Body, Shape, Circle, Segment, Poly

from lib.geom import TriangleMesh


SHAPE_TYPES = {
    "box": {
        #"polygon": [(-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5)],
        "polygon": [(-.49, -.49), (.49, -.49), (.49, .49), (-.49, .49)],
    },
    "circle": {},
}


class Object:

    def __init__(
            self,
            space: Space,
            shape_type: str,
            pos: Tuple[float, float],
            scale: float = 1.,
            mass: float = 1,
            static: bool = False,
            friction: float = 1.,
    ):
        self.space = space
        self.shape_type = shape_type
        self.static = static
        self._scale = scale

        padding = 0.03

        if not static:
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
                self.shape = Circle(self.body, self.scale / 2. - padding)

        # static
        else:
            self.mass = 0
            self.body = self.space.static_body
            self._static_position = Vec2d(*pos)

            if self.shape_type == "box":
                self.shape = Poly(self.space.static_body, [
                    (pos[0] + p[0] * scale, pos[1] + p[1] * scale)
                    for p in SHAPE_TYPES[self.shape_type]["polygon"]
                ])
                self.shape.get_vertices()
            elif self.shape_type == "circle":
                self.shape = Circle(self.space.static_body, self.scale / 2. - padding, offset=pos)

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

    def apply_impulse(self, impulse: Tuple[float, float], point: Optional[Tuple[float, float]] = (0, 0)):
        if not self.static:
            point = self.position + point
            self.body.apply_impulse_at_world_point(impulse, point)

    def add_to_mesh(self, mesh: TriangleMesh):
        offset = self.body.position
        rotation = self.body.angle
        if isinstance(self.shape, Poly):
            vertices = [
                glm.vec3(v.rotated(rotation) + offset, 0)
                for v in self.shape.get_vertices()
            ]

            for i in range(len(vertices) - 1):
                mesh.add_triangle(
                    vertices[0],
                    vertices[i+1],
                    vertices[i],
                )

        elif self.shape_type == "circle":
            num_seg = 4
            center = glm.vec3(offset, 0)
            vertices = [
                glm.vec3(
                    Vec2d(math.sin(s / num_seg * math.pi), math.cos(s / num_seg * math.pi))
                        .rotated(rotation) * self.scale / 2. + offset,
                    0
                )
                for s in range(num_seg*2+1)
            ]
            for i in range(len(vertices) - 1):
                mesh.add_triangle(
                    center,
                    vertices[i+1],
                    vertices[i],
                )

    def update(self, time: float, dt: float):
        pass
        # self.apply_impulse((0, -min(1., dt * 10.)))


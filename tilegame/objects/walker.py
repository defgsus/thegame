import time
import math

import glm

from pyglet import gl

from lib.geom import TriangleMesh, MeshFactory

from ..render.mesh_object import MeshObject
from .object import ObjectBase


class WalkerObject(ObjectBase):

    def __init__(
            self,
            id: str,
            location: glm.vec3 = glm.vec3(0),
            rotation: float = 0,
    ):
        super().__init__(id=id, location=location, rotation=rotation)
        self._walk_time = 0.
        self._walking = 0.  # [0., 1.]
        self._head_rotation = 0.

    @property
    def walking(self) -> float:
        return self._walking

    def walk(self, amount: float):
        amount = max(-1., min(1., amount * 5.))
        norm = self.direction
        self._walking += (1. - self._walking) * abs(amount) / 3.
        self.move(amount * norm * self.walking)

    def turn(self, amount: float):
        self._walking += (1. - self._walking) * min(1, abs(amount) * 3.)
        self._rotation -= amount * self._walking * 100.
        sign = -1 if amount < 0 else 1
        self._head_rotation += (-70*sign - self._head_rotation) * min(1., abs(amount) * 5.)

    def update(self, time: float, dt: float):
        super().update(time, dt)
        self._walk_time += math.pow(self._walking, 1.2) * min(1., dt * 10.)

        t = self._walk_time
        rest_head_rotation = math.sin(t)

        if self.time_since_last_move() > 0.0100:
            self._walking += (0. - self._walking) * min(1., dt * 3.)

            self._head_rotation += (rest_head_rotation - self._head_rotation) * min(1., dt * 3.)
        else:
            self._head_rotation += (rest_head_rotation - self._head_rotation) * min(1., dt * 1.)

    def update_mesh(self, mesh: MeshObject, time: float, dt: float):
        t = self._walk_time
        amount = self._walking

        head = glm.translate(glm.mat4(), glm.vec3(0, 0, 3))
        head = glm.rotate(head, self._head_rotation / 180. * math.pi, glm.vec3(0, 0, 1))
        mesh.part_transforms[0] = head

        d = -1
        for i in range(2):
            rest_pos = glm.vec3(.4 * d, 0.1, 0)
            walk_pos = glm.vec3(.4*d, .3*math.sin(t+d*1.57), 0)
            foot = glm.translate(glm.mat4(), glm.mix(rest_pos, walk_pos, amount))
            foot = glm.scale(foot, glm.vec3(.3, .5, .3))
            mesh.part_transforms[i+1] = foot
            d = 1

    def create_mesh(self) -> MeshObject:
        mesh = TriangleMesh()
        mesh.create_attribute("a_part", 1, 0., gl.GLfloat)
        factory = MeshFactory()

        # head
        mesh.set_attribute_value("a_part", 0.)
        #factory.add_dodecahedron(mesh)
        factory.add_uv_sphere(mesh, .5, num_u=24, num_v=12)
        # eyes
        with factory:
            factory.translate((-.3, .3, .2))
            factory.rotate_z(20)
            factory.add_cylinder(mesh, .2, .3)
        with factory:
            factory.translate((.3, .3, .2))
            factory.rotate_z(-20)
            factory.add_cylinder(mesh, .2, .3)

        # left food
        mesh.set_attribute_value("a_part", 1.)
        factory.add_dodecahedron(mesh)
        # right food
        mesh.set_attribute_value("a_part", 2.)
        factory.add_dodecahedron(mesh)

        return MeshObject(mesh, num_parts=3, name="walker-mesh")

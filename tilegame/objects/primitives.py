import time
import math
from typing import Optional

import glm
from pyglet import gl
import pybullet

from lib.geom import TriangleMesh, MeshFactory

from ..render.mesh_object import MeshObject
from .object import ObjectBase


class Plane(ObjectBase):

    def __init__(
            self,
            id: str,
            physics_client_id: int = 0,
    ):
        super().__init__(
            id=id,
            location=glm.vec3(0, 0, 0),
            rotation=0.,
            physics_client_id=physics_client_id,
        )

    def create_bullet_body(self):
        self._body_id = pybullet.loadURDF("plane.urdf", physicsClientId=self._physics_client_id)


class Sphere(ObjectBase):

    def __init__(
            self,
            id: str,
            location: glm.vec3 = glm.vec3(0, 0, .5),
            radius: float = .5,
            mass: float = 1.,
            physics_client_id: int = 0,
    ):
        super().__init__(
            id=id,
            location=location,
            rotation=0.,
            physics_client_id=physics_client_id,
        )
        self._mass = mass
        self._radius = radius
        self._body_id = None

    def create_bullet_body(self):
        self._shape_id = pybullet.createCollisionShape(
            shapeType=pybullet.GEOM_SPHERE,
            radius=self._radius,
            physicsClientId=self._physics_client_id,
        )
        self._body_id = pybullet.createMultiBody(
            baseMass=self._mass,
            baseCollisionShapeIndex=self._shape_id,
            basePosition=list(self._location),
            baseOrientation=[0, 0, 0, 1],
            physicsClientId=self._physics_client_id,
        )

    def create_mesh(self) -> MeshObject:
        mesh = TriangleMesh()
        mesh.create_attribute("a_part", 1, 0., gl.GLfloat)
        factory = MeshFactory()

        mesh.set_attribute_value("a_part", 0.)
        factory.add_uv_sphere(mesh, .5, num_u=12, num_v=6)

        return MeshObject(mesh, num_parts=3, name=f"{self.id}-mesh")

    def update_mesh(self, mesh: MeshObject, time: float, dt: float):
        pass

    def transformation_matrix(self) -> glm.mat4:
        pos, quat = pybullet.getBasePositionAndOrientation(
            bodyUniqueId=self._body_id,
            physicsClientId=self._physics_client_id,
        )
        mat3 = pybullet.getMatrixFromQuaternion(quat)
        return glm.mat4(
            mat3[0], mat3[3], mat3[6], 0,
            mat3[1], mat3[4], mat3[7], 0,
            mat3[2], mat3[5], mat3[8], 0,
            pos[0], pos[1], pos[2], 1,
        )
        return glm.mat4(
            mat3[0], mat3[1], mat3[2], 0,
            mat3[3], mat3[4], mat3[5], 0,
            mat3[6], mat3[7], mat3[8], 0,
            pos[0], pos[1], pos[2], 1,
        )

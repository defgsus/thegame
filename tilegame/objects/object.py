import time
import math
from typing import Optional

import glm
import pybullet

from ..render.mesh_object import MeshObject


class ObjectBase:

    def __init__(
            self,
            id: str,
            location: glm.vec3 = glm.vec3(0),
            rotation: float = 0,
            physics_client_id: int = 0,
    ):
        self.id = id
        self._location = location
        self._rotation = rotation
        self._last_location = None
        self._last_move_time = 0
        self.average_speed = 0.
        self.direction_of_movement = glm.vec2(0, 1)
        self._physics_client_id = physics_client_id
        self._body_id = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.id}')"

    @property
    def location(self) -> glm.vec3:
        if not self.has_physics:
            return self._location
        pos, quat = pybullet.getBasePositionAndOrientation(
            bodyUniqueId=self._body_id,
            physicsClientId=self._physics_client_id,
        )
        #pos = [0 if p == math.nan else p for p in pos]
        return glm.vec3(pos)

    @property
    def rotation(self) -> float:
        if not self.has_physics:
            return self._rotation
        else:
            pos, quat = pybullet.getBasePositionAndOrientation(
                bodyUniqueId=self._body_id,
                physicsClientId=self._physics_client_id,
            )
            angles = pybullet.getEulerFromQuaternion(quat)
            return angles[2]

    @property
    def direction(self) -> glm.vec2():
        if not self.has_physics:
            a = self._rotation / 180. * math.pi
            return glm.vec2(-math.sin(a), math.cos(a))
        else:
            pos, quat = pybullet.getBasePositionAndOrientation(
                bodyUniqueId=self._body_id,
                physicsClientId=self._physics_client_id,
            )
            mat3 = pybullet.getMatrixFromQuaternion(quat)
            print(
                [round(v, 2) for v in quat],
                [round(v, 2) for v in mat3],
            )
            return glm.vec2(mat3[2], mat3[5])#, mat3[8])

    @property
    def has_physics(self) -> bool:
        return self._body_id is not None

    def time_since_last_move(self) -> float:
        return time.time() - self._last_move_time

    def update(self, time: float, dt: float):
        location = self.location

        if self._last_location is None:
            speed = 0.
        else:
            speed = glm.distance(location.xy, self._last_location.xy) / dt
            if speed:
                self.direction_of_movement = glm.normalize(location.xy - self._last_location.xy)

        self._last_location = self._location.__copy__()

        self.average_speed += min(1., 8. * dt) * (speed - self.average_speed)

    def update_mesh(self, mesh: MeshObject, time: float, dt: float):
        raise NotImplementedError

    def create_mesh(self) -> MeshObject:
        raise NotImplementedError

    def move(self, dir: glm.vec2):
        if not self.has_physics:
            self._location += glm.vec3(dir, 0)
            self._last_move_time = time.time()
        else:
            linear, angular = pybullet.getBaseVelocity(
                bodyUniqueId=self._body_id,
                physicsClientId=self._physics_client_id,
            )
            dir = dir * 10.
            linear = [linear[0] + dir.x, linear[1] + dir.y, linear[2]]
            pybullet.resetBaseVelocity(
                objectUniqueId=self._body_id,
                linearVelocity=linear,
                angularVelocity=angular,
                physicsClientId=self._physics_client_id,
            )

    def rotate(self, degree: float):
        self._last_move_time = time.time()
        if not self.has_physics:
            self._rotation += degree
        else:
            linear, angular = pybullet.getBaseVelocity(
                bodyUniqueId=self._body_id,
                physicsClientId=self._physics_client_id,
            )
            angular = [angular[0], angular[1], angular[2] + degree * .1]
            pybullet.resetBaseVelocity(
                objectUniqueId=self._body_id,
                linearVelocity=linear,
                angularVelocity=angular,
                physicsClientId=self._physics_client_id,
            )

    def transformation_matrix(self) -> glm.mat4:
        if not self.has_physics:
            trans = glm.translate(glm.mat4(1), self._location)
            trans *= glm.rotate(glm.mat4(1), self._rotation / 180 * glm.pi(), glm.vec3(0, 0, 1))
            return trans

        pos, quat = pybullet.getBasePositionAndOrientation(
            bodyUniqueId=self._body_id,
            physicsClientId=self._physics_client_id,
        )
        mat3 = pybullet.getMatrixFromQuaternion(quat)
        return glm.rotate(glm.mat4(
            mat3[0], mat3[3], mat3[6], 0,
            mat3[1], mat3[4], mat3[7], 0,
            mat3[2], mat3[5], mat3[8], 0,
            pos[0], pos[1], pos[2], 1,
        ), math.pi/2., [1, 0, 0])

    def create_bullet_body(self):
        raise NotImplementedError

        if not self.urdf_filename:
            return None

        self.bullet_id = pybullet.loadURDF(self.urdf_filename, physicsClientId=client_id)
        return self.bullet_id

import time
import math

import glm

from ..render.mesh_object import MeshObject


class ObjectBase:

    def __init__(
            self,
            id: str,
            location: glm.vec3 = glm.vec3(0),
            rotation: float = 0,
    ):
        self.id = id
        self._location = location
        self._rotation = rotation
        self._last_location = None
        self._last_move_time = 0
        self.average_speed = 0.
        self.direction_of_movement = glm.vec2(0, 1)

    @property
    def location(self) -> glm.vec3:
        return self._location

    @property
    def rotation(self) -> float:
        return self._rotation

    @property
    def direction(self) -> glm.vec2():
        a = self._rotation / 180. * math.pi
        return glm.vec2(-math.sin(a), math.cos(a))

    def time_since_last_move(self) -> float:
        return time.time() - self._last_move_time

    def update(self, time: float, dt: float):
        if self._last_location is None:
            speed = 0.
        else:
            speed = glm.distance(self._location, self._last_location) / dt
            if speed:
                self.direction_of_movement = glm.normalize(self._location.xy - self._last_location.xy)

        self._last_location = self._location.__copy__()

        self.average_speed += 8. * dt * (speed - self.average_speed)

    def update_mesh(self, mesh: MeshObject, time: float, dt: float):
        raise NotImplementedError

    def create_mesh(self) -> MeshObject:
        raise NotImplementedError

    def move(self, dir: glm.vec2):
        self._location += glm.vec3(dir, 0)
        self._last_move_time = time.time()

    def rotate(self, degree: float):
        self._rotation += degree
        self._last_move_time = time.time()

    def transformation_matrix(self) -> glm.mat4:
        trans = glm.translate(glm.mat4(1), self._location)
        trans *= glm.rotate(glm.mat4(1), self._rotation / 180 * glm.pi(), glm.vec3(0, 0, 1))
        return trans


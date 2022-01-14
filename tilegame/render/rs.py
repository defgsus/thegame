import glm
import math

from lib.opengl import RenderSettings


class GameProjection:

    def __init__(self):
        self._trans = glm.mat3(1)
        self.scale = 10.
        self.rotation = 0.
        self.location = glm.vec3(0)

    def transformation_matrix(self) -> glm.mat3:
        m = self._trans * rotation_matrix_2d(self.rotation)
        m *= self.scale * .5
        m[2][0] = self.location.x
        m[2][1] = self.location.y
        return m


def rotation_matrix_2d(degree: float) -> glm.mat3:
    a = degree / 180. * math.pi
    sa = math.sin(a)
    ca = math.cos(a)
    return glm.mat3(
        ca, sa, 0,
        -sa, ca, 0,
        0, 0, 1
    )


class GameRenderSettings(RenderSettings):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.projection = GameProjection()

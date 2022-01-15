import glm
import math

from lib.opengl import RenderSettings


class GameProjection:

    def __init__(self):
        self.scale = 10.
        self.rotation = 0.
        self.location = glm.vec3(0)
        self._stack = []

    def transformation_matrix(self) -> glm.mat3:
        m = rotation_matrix_2d(self.rotation)
        m *= self.scale * .5
        m[2][0] = self.location.x
        m[2][1] = self.location.y
        return m

    def push(self):
        self._stack.append({
            "scale": self.scale,
            "rotation": self.rotation,
            "location": self.location.__copy__(),
        })

    def pop(self):
        s = self._stack.pop(-1)
        self.scale = s["scale"]
        self.rotation = s["rotation"]
        self.location = s["location"]

    def __enter__(self):
        self.push()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pop()


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

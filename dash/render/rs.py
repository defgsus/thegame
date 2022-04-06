import glm
import math

from lib.opengl import RenderSettings


class GameProjection:

    def __init__(self, rs: "GameRenderSettings"):
        self.rs = rs
        self.scale = 10.
        self.rotation_deg = 0.
        self.location = glm.vec3(0)
        self._stack = []

    def projection_matrix_4(self) -> glm.mat4:
        scale = 1.
        ratio = self.rs.render_width / self.rs.render_height
        m = glm.ortho(-scale * ratio, scale * ratio, -scale, scale, -10, 10)
        return m

    def transformation_matrix_4(self) -> glm.mat4:
        m = glm.rotate(
            glm.mat4(1), -self.rotation_deg / 180 * glm.pi(), glm.vec3(0, 0, 1)
        )
        m = m * glm.scale(glm.mat4(), glm.vec3(2. / self.scale))
        m = m * glm.translate(glm.mat4(), glm.vec3(-self.location.x, -self.location.y, 0))
        return m

    def transformation_matrix(self) -> glm.mat3:
        m = rotation_matrix_2d(self.rotation_deg)
        m *= self.scale * .5
        m[2][0] = self.location.x
        m[2][1] = self.location.y
        return m

    def push(self):
        self._stack.append({
            "scale": self.scale,
            "rotation": self.rotation_deg,
            "location": self.location.__copy__(),
        })

    def pop(self):
        s = self._stack.pop(-1)
        self.scale = s["scale"]
        self.rotation_deg = s["rotation"]
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
        self.projection = GameProjection(self)

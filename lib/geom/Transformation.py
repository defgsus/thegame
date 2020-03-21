import glm

from lib.pector.const import DEG_TO_TWO_PI


class Transformation:
    """
    A transformation matrix with easy to use functions and
    supporting the `with` statement
    """
    def __init__(self, transformation=None):
        self._trans = transformation or glm.mat4(1)
        self._trans_stack = []

    def push(self):
        """Push current transformation on stack"""
        self._trans_stack.append(glm.mat4(self._trans))

    def pop(self):
        """Pop transformation from stack - if possible"""
        if self._trans_stack:
            self._trans = self._trans_stack.pop()

    def __enter__(self):
        self.push()
        return self

    @property
    def matrix(self):
        return self._trans

    @matrix.setter
    def matrix(self, matrix):
        self._trans = matrix

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pop()

    def translate(self, pos):
        self._trans = glm.translate(self._trans, glm.vec3(pos))

    def rotate(self, axis, angle):
        self._trans = glm.rotate(self._trans, angle * DEG_TO_TWO_PI, glm.vec3(axis))

    def rotate_x(self, angle):
        self.rotate((1, 0, 0), angle)

    def rotate_y(self, angle):
        self.rotate((0, 1, 0), angle)

    def rotate_z(self, angle):
        self.rotate((0, 0, 1), angle)

    def scale(self, factor):
        self._trans = glm.scale(self._trans, glm.vec3(factor))

    def look(self, direction, up):
        quat = glm.quatLookAt(glm.vec3(direction), glm.vec3(up))
        self._trans = glm.rotate(self._trans, glm.angle(quat), glm.axis(quat))

    # TODO: not really working
    def align_direction(self, old_dir, new_dir):
        norm = glm.vec3(new_dir)
        up = glm.vec3(old_dir)
        c = glm.cross(norm, up)
        up = glm.cross(c, norm)

        quat = glm.quatLookAt(up, norm)
        self._trans = glm.rotate(self._trans, glm.angle(quat), glm.axis(quat))

    def transform(self, pos):
        """Transform the 3d-vector with the current transformation"""
        return (self._trans * glm.vec4(pos, 1)).xyz

    def transform_direction(self, dir):
        """Transform the 3d-vector with the current transformation, excluding translations"""
        return (self._trans * glm.vec4(dir, 0)).xyz

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

    def transform(self, pos):
        """Transform the 3d-vector with the current translation"""
        return (self._trans * glm.vec4(pos, 1)).xyz

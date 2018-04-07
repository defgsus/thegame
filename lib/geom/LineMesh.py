import math
import glm
from lib.pector import *
from lib.opengl.Drawable import Drawable, GL_TRIANGLES, GL_LINES


def vecs_to_list(vecs):
    r = []
    for vec in vecs:
        try:
            for v in vec:
                r.append(v)
        except TypeError:
            r.append(vec)
    return r


class AbstractLineMesh:

    def is_empty(self):
        raise NotImplementedError

    def vertices_array(self):
        raise NotImplementedError

    def colors_array(self):
        raise NotImplementedError

    def lines_array(self):
        raise NotImplementedError

    def add_line(self, pos1, pos2):
        return self.add_line_idx(
            self.add_vertex(pos1),
            self.add_vertex(pos2),
        )

    def create_drawable(self):
        draw = Drawable()
        return self.update_drawable(draw)

    def update_drawable(self, draw):
        draw.clear()
        a = self.vertices_array()
        if not a:
            raise ValueError("No vertices to make drawable")
        draw.set_attribute(draw.A_POSITION, 3, a)

        a = self.colors_array()
        if a:
            draw.set_attribute(draw.A_COLOR, 3, a)

        a = self.lines_array()
        if a:
            draw.set_index(GL_LINES, a)
        return draw

    def add_cube(self, center, size):
        c = glm.vec3(center)
        s = glm.vec3(size) / 2.

        verts = (
            ((-s.x, -s.y, -s.z), (+s.x, -s.y, -s.z)),
            ((-s.x, +s.y, -s.z), (+s.x, +s.y, -s.z)),
            ((-s.x, -s.y, +s.z), (+s.x, -s.y, +s.z)),
            ((-s.x, +s.y, +s.z), (+s.x, +s.y, +s.z)),

            ((-s.x, -s.y, -s.z), (-s.x, +s.y, -s.z)),
            ((+s.x, -s.y, -s.z), (+s.x, +s.y, -s.z)),
            ((-s.x, -s.y, +s.z), (-s.x, +s.y, +s.z)),
            ((+s.x, -s.y, +s.z), (+s.x, +s.y, +s.z)),

            ((-s.x, -s.y, -s.z), (-s.x, -s.y, +s.z)),
            ((+s.x, -s.y, -s.z), (+s.x, -s.y, +s.z)),
            ((-s.x, +s.y, -s.z), (-s.x, +s.y, +s.z)),
            ((+s.x, +s.y, -s.z), (+s.x, +s.y, +s.z)),

        )
        for v in verts:
            self.add_line(c+v[0], c+v[1])



class LineMesh(AbstractLineMesh):
    def __init__(self):
        self._vertices = []
        self._colors = []
        self._lines = []
        self._color = (1,1,1)

    def is_empty(self):
        return len(self._lines) == 0

    def set_color(self, r, g, b):
        self._color = (r, g, b)

    def add_vertex(self, pos):
        self._vertices.append(pos)
        self._colors.append(self._color)
        return len(self._vertices)-1

    def add_line_idx(self, i1, i2):
        self._lines.append((i1, i2))
        return len(self._lines)-1

    def vertices_array(self):
        return vecs_to_list(self._vertices)

    def colors_array(self):
        return vecs_to_list(self._colors)

    def lines_array(self):
        return vecs_to_list(self._lines)


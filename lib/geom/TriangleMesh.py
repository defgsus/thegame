import math
from lib.pector import *
from lib.opengl.Drawable import Drawable, GL_TRIANGLES, GL_LINES


class TriangleMesh:
    def __init__(self):
        # mapping (x,y,z) -> vertex_index
        self._vertices = dict()
        self._idx_to_vertex = dict()
        # mapping (i1,i2,i3) -> triangle_index
        self._triangles = dict()
        self._lines = dict()
        # smallest difference between vertex positions
        self.threshold = 0.001

    def pos_to_hash(self, pos):
        return tuple(math.floor(p / self.threshold) * self.threshold for p in pos)

    @staticmethod
    def vecs_to_list(vecs):
        r = []
        for vec in vecs:
            for v in vec:
                r.append(v)
        return r

    def add_vertex(self, pos):
        h = self.pos_to_hash(pos)
        if h in self._vertices:
            return self._vertices[h]
        idx = len(self._vertices)
        self._vertices[h] = idx
        self._idx_to_vertex[idx] = h
        return idx

    def add_triangle_idx(self, i1, i2, i3):
        if i1 == i2 or i1 == i3 or i2 == i3:
            return None
        h = (i1, i2, i3)
        if h in self._triangles:
            return self._triangles[h]
        idx = len(self._triangles)
        self._triangles[h] = idx
        return idx

    def add_triangle(self, pos1, pos2, pos3):
        return self.add_triangle_idx(
            self.add_vertex(pos1),
            self.add_vertex(pos2),
            self.add_vertex(pos3),
        )

    def add_line_idx(self, i1, i2):
        if i1 == i2:
            return None
        h = (i1, i2)
        if h in self._lines:
            return self._lines[h]
        idx = len(self._lines)
        self._lines[h] = idx
        return idx

    def add_line(self, pos1, pos2):
        return self.add_line_idx(
            self.add_vertex(pos1),
            self.add_vertex(pos2),
        )

    def vertices_array(self):
        return self.vecs_to_list(sorted(self._vertices, key=lambda h: self._vertices[h]))

    def triangles_array(self):
        return self.vecs_to_list(sorted(self._triangles, key=lambda h: self._triangles[h]))

    def lines_array(self):
        return self.vecs_to_list(sorted(self._lines, key=lambda h: self._lines[h]))

    def normals_array(self):
        normals = dict()
        for tri in self._triangles:
            (p1, p2, p3) = (self._idx_to_vertex[i] for i in tri)
            norm = vec3(p2) - p1
            norm.cross(vec3(p3) - p1)
            norm.normalize_safe()
            normals[p1] = norm
            normals[p2] = norm
            normals[p3] = norm
        return self.vecs_to_list(normals[p] for p in sorted(normals, key=lambda h: self._vertices[h]))

    def get_drawable(self):
        draw = Drawable()
        #print(self.vertices_array())
        #print(self.triangles_array())
        #print(self.lines_array())
        #print(self.normals_array())
        draw.set_attribute(draw.A_POSITION, 3, self.vertices_array())
        draw.set_attribute(draw.A_NORMAL, 3, self.normals_array())
        if self._triangles:
            draw.set_index(GL_TRIANGLES, self.triangles_array())
        if self._lines:
            draw.set_index(GL_LINES, self.lines_array())
        return draw

    def create_height_map(self, width, height, function, scale=1.,
                          do_triangles=True, do_lines=False):
        heights = []
        for j in range(height+1):
            heights.append([function(i, j) for i in range(width+1)])
        for j in range(height):
            y1 = (j+.1) * scale
            y2 = (j+.9) * scale
            for i in range(width):
                x1 = (i+.03) * scale
                x2 = (i+.97) * scale
                if do_triangles:
                    self.add_triangle(
                        [x1, y1, heights[j][i]],
                        [x2, y1, heights[j][i+1]],
                        [x2, y2, heights[j+1][i+1]],
                    )
                    self.add_triangle(
                        [x1, y1, heights[j][i]],
                        [x2, y2, heights[j+1][i+1]],
                        [x1, y2, heights[j+1][i]],
                    )
                if do_lines:
                    self.add_line([x1, y1, heights[j][i]],
                                  [x2, y1, heights[j][i+1]])
                    self.add_line([x2, y1, heights[j][i+1]],
                                  [x2, y2, heights[j+1][i+1]])

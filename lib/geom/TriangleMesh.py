import math
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


class AbstractTriangleMesh:

    def vertices_array(self):
        raise NotImplementedError

    def texcoords_array(self):
        raise NotImplementedError

    def triangles_array(self):
        raise NotImplementedError

    def quads_array(self):
        raise NotImplementedError

    def lines_array(self):
        raise NotImplementedError

    def normals_array(self):
        raise NotImplementedError

    def add_triangle(self, pos1, pos2, pos3,
                     tex1=(0,0), tex2=(1,0), tex3=(1,1)):
        i1 = self.add_vertex(pos1)
        i2 = self.add_vertex(pos2)
        i3 = self.add_vertex(pos3)
        self.add_texcoord(tex1)
        self.add_texcoord(tex2)
        self.add_texcoord(tex3)
        return self.add_triangle_idx(i1, i2, i3)

    def add_quad(self, pos1, pos2, pos3, pos4,
                       tex1=(0,0), tex2=(1,0), tex3=(1,1), tex4=(0,1)):
        self.add_triangle(pos1, pos2, pos3, tex1, tex2, tex3)
        return self.add_triangle(pos1, pos3, pos4, tex1, tex3, tex4)
        # TODO
        self.add_texcoord(tex1)
        self.add_texcoord(tex2)
        self.add_texcoord(tex3)
        self.add_texcoord(tex4)
        return self.add_quad_idx(
            self.add_vertex(pos1),
            self.add_vertex(pos2),
            self.add_vertex(pos3),
            self.add_vertex(pos4),
        )

    def add_line(self, pos1, pos2):
        return self.add_line_idx(
            self.add_vertex(pos1),
            self.add_vertex(pos2),
        )

    def get_drawable(self):
        draw = Drawable()
        #print(self.vertices_array())
        #print(self.triangles_array())
        #print(self.lines_array())
        #print(self.normals_array())
        a = self.vertices_array()
        if not a:
            raise ValueError("No vertices to make drawable")
        draw.set_attribute(draw.A_POSITION, 3, a)

        a = self.normals_array()
        if a:
            draw.set_attribute(draw.A_NORMAL, 3, a)

        a = self.texcoords_array()
        if a:
            draw.set_attribute(draw.A_TEXCOORD, 2, a)

        a = self.triangles_array()
        if a:
            draw.set_index(GL_TRIANGLES, a)

        a = self.quads_array()
        if a:
            tris = []
            for i in range(0, len(a), 4):
                tris.append(a[i])
                tris.append(a[i+1])
                tris.append(a[i+2])
                tris.append(a[i])
                tris.append(a[i+2])
                tris.append(a[i+2])
            draw.set_index(GL_TRIANGLES, tris)

        a = self.lines_array()
        if a:
            draw.set_index(GL_LINES, a)
        return draw

    def create_height_map(self, width, height, function, scale=1.,
                          do_triangles=True, do_lines=False):
        heights = []
        for j in range(height+1):
            heights.append([function(i, j) for i in range(width+1)])
        hh = height/2.
        wh = width/2.
        for j in range(height):
            y1 = (j-hh) * scale
            y2 = (j+1-hh) * scale
            for i in range(width):
                x1 = (i-wh) * scale
                x2 = (i+1-wh) * scale
                h1 = heights[j][i]
                hb = heights[j+1][i]
                hf = heights[j-1][i]
                h3 = heights[j][i+1]
                if do_triangles:
                    self.add_quad([x1, y1, h1], [x2, y1, h1], [x2, y2, h1], [x1, y2, h1])
                    self.add_quad([x1, y2, h1], [x2, y2, h1], [x2, y2, hb], [x1, y2, hb])

                    self.add_quad([x2, y2, h1], [x2, y1, h1], [x2, y1, h3], [x2, y2, h3])

                if do_lines:
                    pass

    def create_height_map_uneven(self, width, height, function, scale=1.,
                                 do_triangles=True, do_lines=False):
        heights = []
        for j in range(height+1):
            heights.append([function(i, j) for i in range(width+1)])
        hh = height/2.
        wh = width/2.
        for j in range(height):
            y1 = (j-hh) * scale
            y2 = (j+1-hh) * scale
            for i in range(width):
                x1 = (i-wh) * scale
                x2 = (i+1-wh) * scale
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


class TriangleMesh(AbstractTriangleMesh):
    """Merges nearby vertex positions"""
    def __init__(self):
        self._vertices = []
        self._texcoords = []
        self._triangles = []
        self._lines = []
        self._quads = []

    def add_vertex(self, pos):
        self._vertices.append(pos)
        return len(self._vertices)-1

    def add_texcoord(self, uv):
        self._texcoords.append(uv)
        return len(self._texcoords)-1

    def add_triangle_idx(self, i1, i2, i3):
        if i1 == i2 or i1 == i3 or i2 == i3:
            return None
        self._triangles.append((i1, i2, i3))
        return len(self._triangles)-1

    def add_quad_idx(self, i1, i2, i3, i4):
        self.add_triangle_idx(i1, i2, i3)
        return self.add_triangle_idx(i1, i3, i4)
        # TODO
        #self._quads.append((i1, i2, i3, i4))
        #return len(self._quads)-1

    def add_line_idx(self, i1, i2):
        self._lines.append((i1, i2))
        return len(self._lines)-1

    def vertices_array(self):
        return vecs_to_list(self._vertices)

    def texcoords_array(self):
        return vecs_to_list(self._texcoords)

    def triangles_array(self):
        return vecs_to_list(self._triangles)

    def quads_array(self):
        return vecs_to_list(self._quads)

    def lines_array(self):
        return vecs_to_list(self._lines)

    def normals_array(self):
        normals = [vec3(0.)] * len(self._vertices)
        for tri in self._triangles:
            (p1, p2, p3) = (self._vertices[i] for i in tri)
            norm = vec3(p2) - p1
            norm.cross(vec3(p3) - p1)
            norm.normalize_safe()
            for i in tri:
                normals[i] = norm
        return vecs_to_list(normals)


class TriangleHashMesh(AbstractTriangleMesh):
    """Merges nearby vertex positions"""
    def __init__(self, threshold=0.001):
        # mapping (x,y,z) -> vertex_index
        self._vertices = dict()
        self._idx_to_vertex = dict()
        # mapping (i1,i2,i3) -> triangle_index
        self._triangles = dict()
        self._lines = dict()
        self._quads = dict()
        # smallest difference between vertex positions
        self.threshold = threshold

    def pos_to_hash(self, pos):
        return tuple(math.floor(p / self.threshold) * self.threshold for p in pos)

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

    def add_quad_idx(self, i1, i2, i3, i4):
        # TODO
        self.add_triangle_idx(i1, i2, i3)
        return self.add_triangle_idx(i1, i3, i4)
        if i1 == i2 or i1 == i3 or i2 == i3 or i1==i4 or i2==i3 or i3==i4:
            return None
        h = (i1, i2, i3, i4)
        if h in self._quads:
            return self._quads[h]
        idx = len(self._quads)
        self._quads[h] = idx
        return idx

    def add_line_idx(self, i1, i2):
        if i1 == i2:
            return None
        h = (i1, i2)
        if h in self._lines:
            return self._lines[h]
        idx = len(self._lines)
        self._lines[h] = idx
        return idx

    def vertices_array(self):
        return vecs_to_list(sorted(self._vertices, key=lambda h: self._vertices[h]))

    def triangles_array(self):
        return vecs_to_list(sorted(self._triangles, key=lambda h: self._triangles[h]))

    def quads_array(self):
        return vecs_to_list(sorted(self._quads, key=lambda h: self._quads[h]))

    def lines_array(self):
        return vecs_to_list(sorted(self._lines, key=lambda h: self._lines[h]))

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
        return vecs_to_list(normals[p] for p in sorted(normals, key=lambda h: self._vertices[h]))


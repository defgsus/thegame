import glm
from .TriangleMesh import TriangleMesh


class Polygons:

    class Triangle:
        def __init__(self, p1, p2, p3):
            self.p1 = glm.vec3(p1)
            self.p2 = glm.vec3(p2)
            self.p3 = glm.vec3(p3)
            self.normal = self.p2 - self.p1
            self.normal = glm.cross(self.normal, self.p3 - self.p1)
            self.normal = glm.normalize(self.normal)

    class Quad:
        def __init__(self, p1, p2, p3, p4):
            self.p1 = glm.vec3(p1)
            self.p2 = glm.vec3(p2)
            self.p3 = glm.vec3(p3)
            self.p4 = glm.vec3(p4)
            self.normal = self.p2 - self.p1
            self.normal = glm.cross(self.normal, self.p3 - self.p1)
            self.normal = glm.normalize(self.normal)

    def __init__(self):
        self._triangles = []
        self._quads = []

    def add_triangle(self, pos1, pos2, pos3):
        t = self.Triangle(pos1, pos2, pos3)
        self._triangles.append(t)
        return t

    def add_quad(self, pos1, pos2, pos3, pos4):
        t = self.Quad(pos1, pos2, pos3, pos4)
        self._quads.append(t)
        return t

    def extrude(self, offset):
        triangles = self._triangles
        quads = self._quads

        self._triangles = []
        self._quads = []

        for poly in triangles:
            poly_offset = offset * poly.normal
            n1 = poly.p1 + poly_offset
            n2 = poly.p2 + poly_offset
            n3 = poly.p3 + poly_offset

            self.add_quad(poly.p1, poly.p2, n2, n1)
            self.add_quad(poly.p2, poly.p3, n3, n2)
            self.add_quad(poly.p3, poly.p1, n1, n3)
            self.add_triangle(n1, n2, n3)

        for poly in quads:
            poly_offset = offset * poly.normal
            n1 = poly.p1 + poly_offset
            n2 = poly.p2 + poly_offset
            n3 = poly.p3 + poly_offset
            n4 = poly.p4 + poly_offset

            self.add_quad(poly.p1, poly.p2, n2, n1)
            self.add_quad(poly.p2, poly.p3, n3, n2)
            self.add_quad(poly.p3, poly.p4, n4, n3)
            self.add_quad(poly.p4, poly.p1, n1, n4)
            self.add_quad(n1, n2, n3, n4)

    def create_mesh(self):
        mesh = TriangleMesh()
        for tri in self._triangles:
            mesh.add_triangle(tri.p1, tri.p2, tri.p3)
        for quad in self._quads:
            mesh.add_quad(quad.p1, quad.p2, quad.p3, quad.p4)
        return mesh

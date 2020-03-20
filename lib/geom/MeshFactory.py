import math

import glm

from .TriangleMesh import TriangleMesh
from .LineMesh import LineMesh
from lib.pector.const import PI, TWO_PI, DEG_TO_TWO_PI


class MeshFactory:
    
    def __init__(self, transformation=None):
        self._trans = transformation or glm.mat4(1)
        self._trans_stack = []

    def push(self):
        self._trans_stack.append(self._trans.copy())

    def pop(self):
        if self._trans_stack:
            self._trans = self._trans_stack.pop()

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
        self._trans = glm.scale(self._trans, factor)

    def transform(self, pos):
        return (self._trans * glm.vec4(pos, 1)).xyz

    def add_triangle(self, mesh, p1, p2, p3):
        p1 = self.transform(p1)
        p2 = self.transform(p2)
        p3 = self.transform(p3)
        mesh.add_triangle(p1, p2, p3)

    def add_quad(self, mesh, p1, p2, p3, p4):
        p1 = self.transform(p1)
        p2 = self.transform(p2)
        p3 = self.transform(p3)
        p4 = self.transform(p4)
        if hasattr(mesh, "add_quad"):
            mesh.add_quad(p1, p2, p3, p4)
        else:
            mesh.add_triangle(p1, p2, p3)
            mesh.add_triangle(p1, p3, p4)

    def add_cube(self, mesh, size=(1, 1, 1), origin=(0, 0, 0)):
        r = glm.vec3(size) / 2.
        o = glm.vec3(origin)
        
        # front
        self.add_quad(mesh, o+(-r.x,-r.y, r.z), o+( r.x,-r.y, r.z), o+( r.x, r.y, r.z), o+(-r.x, r.y, r.z))
        # left
        self.add_quad(mesh, o+(-r.x,-r.y,-r.z), o+(-r.x,-r.y, r.z), o+(-r.x, r.y, r.z), o+(-r.x, r.y,-r.z))
        # right
        self.add_quad(mesh, o+( r.x,-r.y, r.z), o+( r.x,-r.y,-r.z), o+( r.x, r.y,-r.z), o+( r.x, r.y, r.z))
        # back
        self.add_quad(mesh, o+( r.x,-r.y,-r.z), o+(-r.x,-r.y,-r.z), o+(-r.x, r.y,-r.z), o+( r.x, r.y,-r.z))
        # top
        self.add_quad(mesh, o+(-r.x, r.y, r.z), o+( r.x, r.y, r.z), o+( r.x, r.y,-r.z), o+(-r.x, r.y,-r.z))
        # bottom
        self.add_quad(mesh, o+(-r.x,-r.y,-r.z), o+( r.x,-r.y,-r.z), o+( r.x,-r.y, r.z), o+(-r.x,-r.y, r.z))

    def add_cube_XXX(self, mesh, size=(1, 1, 1), origin=(0, 0, 0)):
        r = glm.vec3(size) / 2.
        o = glm.vec3(origin)

        # front
        self.add_quad(mesh, o+(-r.x,-r.y,-r.z), o+( r.x,-r.y,-r.z), o+( r.x, r.y,-r.z), o+(-r.x, r.y,-r.z))
        # left
        self.add_quad(mesh, o+(-r.x,-r.y, r.z), o+(-r.x,-r.y,-r.z), o+(-r.x, r.y,-r.z), o+(-r.x, r.y, r.z))
        # right
        self.add_quad(mesh, o+( r.x,-r.y,-r.z), o+( r.x,-r.y, r.z), o+( r.x, r.y, r.z), o+( r.x, r.y,-r.z))
        # back
        self.add_quad(mesh, o+( r.x,-r.y, r.z), o+(-r.x,-r.y, r.z), o+(-r.x, r.y, r.z), o+( r.x, r.y, r.z))
        # top
        self.add_quad(mesh, o+(-r.x, r.y,-r.z), o+( r.x, r.y,-r.z), o+( r.x, r.y, r.z), o+(-r.x, r.y, r.z))
        # bottom
        self.add_quad(mesh, o+(-r.x,-r.y, r.z), o+( r.x,-r.y, r.z), o+( r.x,-r.y,-r.z), o+(-r.x,-r.y,-r.z))

    def add_uv_sphere(self, mesh, radius=1, num_u=5, num_v=5, origin=(0, 0, 0)):
        o = glm.vec3(origin)

        def _sphere_point(u, v):
            u = u / num_u * TWO_PI
            v = v / num_v * PI
            p = glm.vec3(-math.sin(v), math.cos(v), 0)
            p.z = -p.x * math.sin(u)
            p.x = p.x * math.cos(u)
            return p * radius + o

        for u in range(num_u):
            p1 = _sphere_point(u, 0)
            p2 = _sphere_point(u-1, 1)
            p3 = _sphere_point(u, 1)
            self.add_triangle(mesh, p1, p2, p3)

        for v in range(1, num_v):
            for u in range(num_u):
                p1 = _sphere_point(u, v)
                p2 = _sphere_point(u-1, v)
                p3 = _sphere_point(u-1, v+1)
                p4 = _sphere_point(u, v+1)
                self.add_quad(mesh, p1, p2, p3, p4)

        for u in range(num_u):
            p1 = _sphere_point(u, num_v-1)
            p2 = _sphere_point(u-1, num_v-1)
            p3 = _sphere_point(u, num_v)
            self.add_triangle(mesh, p1, p2, p3)

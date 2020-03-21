import math

import glm

from .TriangleMesh import TriangleMesh
from .LineMesh import LineMesh
from .Transformation import Transformation
from lib.pector.const import PI, TWO_PI, DEG_TO_TWO_PI


class MeshFactory(Transformation):

    """
    Collection of functions that create objects through triangles, quads, ...
    """
    
    def __init__(self, transformation=None):
        Transformation.__init__(self, transformation=transformation)

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

    def add_pentagon(self, mesh, p1, p2, p3, p4, p5):
        p1 = self.transform(p1)
        p2 = self.transform(p2)
        p3 = self.transform(p3)
        p4 = self.transform(p4)
        p5 = self.transform(p5)
        self.add_triangle(mesh, p1, p2, p5)
        self.add_triangle(mesh, p2, p3, p5)
        self.add_triangle(mesh, p5, p3, p4)

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

    def add_octahedron(self, mesh):
        a = 0.5 / math.sqrt(2. * math.sqrt(2))
        b = 0.5

        p0 = glm.vec3( 0,  b,  0)
        p1 = glm.vec3(-a,  0,  a)
        p2 = glm.vec3( a,  0,  a)
        p3 = glm.vec3( a,  0, -a)
        p4 = glm.vec3(-a,  0, -a)
        p5 = glm.vec3( 0, -b,  0)

        self.add_triangle(mesh, p0, p1, p2)
        self.add_triangle(mesh, p0, p2, p3)
        self.add_triangle(mesh, p0, p3, p4)
        self.add_triangle(mesh, p0, p4, p1)
        self.add_triangle(mesh, p5, p2, p1)
        self.add_triangle(mesh, p5, p3, p2)
        self.add_triangle(mesh, p5, p4, p3)
        self.add_triangle(mesh, p5, p1, p4)

    def add_icosahedron(self, mesh):
        p = self.get_icosahedron_positions()

        self.add_triangle(mesh, p[0], p[2], p[1])
        self.add_triangle(mesh, p[3], p[1], p[2])
        self.add_triangle(mesh, p[3], p[5], p[4])
        self.add_triangle(mesh, p[3], p[4], p[8])
        self.add_triangle(mesh, p[0], p[7], p[6])
        self.add_triangle(mesh, p[0], p[6], p[9])
        self.add_triangle(mesh, p[4], p[11], p[10])
        self.add_triangle(mesh, p[6], p[10], p[11])
        self.add_triangle(mesh, p[2], p[9], p[5])
        self.add_triangle(mesh, p[11], p[5], p[9])
        self.add_triangle(mesh, p[1], p[8], p[7])
        self.add_triangle(mesh, p[10], p[7], p[8])
        self.add_triangle(mesh, p[3], p[2], p[5])
        self.add_triangle(mesh, p[3], p[8], p[1])
        self.add_triangle(mesh, p[0], p[9], p[2])
        self.add_triangle(mesh, p[0], p[1], p[7])
        self.add_triangle(mesh, p[6], p[11], p[9])
        self.add_triangle(mesh, p[6], p[7], p[10])
        self.add_triangle(mesh, p[4], p[5], p[11])
        self.add_triangle(mesh, p[4], p[10], p[8])

    def add_dodecahedron(self, mesh):
        phi = (1. + math.sqrt(5.)) / 2.
        a = 0.5
        b = 0.5 / phi
        c = 0.5 * (2. - phi)

        self.add_pentagon(
            mesh,
            glm.vec3(c, 0, a),
            glm.vec3(b, b, b),
            glm.vec3(0, a, c),
            glm.vec3(-b, b, b),
            glm.vec3(-c, 0, a),
        )
        self.add_pentagon(
            mesh,
            glm.vec3(-c, 0, a),
            glm.vec3(-b, -b, b),
            glm.vec3(0, -a, c),
            glm.vec3(b, -b, b),
            glm.vec3(c, 0, a),
        )
        self.add_pentagon(
            mesh,
            glm.vec3(c, 0, -a),
            glm.vec3(b, -b, -b),
            glm.vec3(0, -a, -c),
            glm.vec3(-b, -b, -b),
            glm.vec3(-c, 0, -a),
        )
        self.add_pentagon(
            mesh,
            glm.vec3(-c, 0, -a),
            glm.vec3(-b, b, -b),
            glm.vec3(0, a, -c),
            glm.vec3(b, b, -b),
            glm.vec3(c, 0, -a),
        )
        self.add_pentagon(
            mesh,
            glm.vec3(0, a, -c),  
            glm.vec3(0, a, c),  
            glm.vec3(b, b, b),  
            glm.vec3(a, c, 0),  
            glm.vec3(b, b, -b),
        )
        self.add_pentagon(
            mesh,
            glm.vec3(0, a, c),  
            glm.vec3(0, a, -c),  
            glm.vec3(-b, b, -b),  
            glm.vec3(-a, c, 0),  
            glm.vec3(-b, b, b),
        )
        self.add_pentagon(
            mesh,
            glm.vec3(0, -a, -c),  
            glm.vec3(0, -a, c),  
            glm.vec3(-b, -b, b),  
            glm.vec3(-a, -c, 0),  
            glm.vec3(-b, -b, -b),
        )
        self.add_pentagon(
            mesh,
            glm.vec3(0, -a, c),  
            glm.vec3(0, -a, -c),  
            glm.vec3(b, -b, -b),  
            glm.vec3(a, -c, 0),  
            glm.vec3(b, -b, b),
        )
        self.add_pentagon(
            mesh,
            glm.vec3(a, c, 0),
            glm.vec3(b, b, b),
            glm.vec3(c, 0, a),
            glm.vec3(b, -b, b),
            glm.vec3(a, -c, 0),
        )
        self.add_pentagon(
            mesh,
            glm.vec3(a, -c, 0),
            glm.vec3(b, -b, -b),
            glm.vec3(c, 0, -a),
            glm.vec3(b, b, -b),
            glm.vec3(a, c, 0),
        )
        self.add_pentagon(
            mesh,
            glm.vec3(-a, c, 0),
            glm.vec3(-b, b, -b),
            glm.vec3(-c, 0, -a),
            glm.vec3(-b, -b, -b),
            glm.vec3(-a, -c, 0),
        )
        self.add_pentagon(
            mesh,
            glm.vec3(-a, -c, 0),
            glm.vec3(-b, -b, b),
            glm.vec3(-c, 0, a),
            glm.vec3(-b, b, b),
            glm.vec3(-a, c, 0),
        )

    @classmethod
    def get_icosahedron_positions(cls):
        a = 0.5
        b = 1. / (1. + math.sqrt(5.))

        return [
            glm.vec3(  0,  b, -a ),
            glm.vec3(  b,  a,  0 ),
            glm.vec3( -b,  a,  0 ),
            glm.vec3(  0,  b,  a ),
            glm.vec3(  0, -b,  a ),
            glm.vec3( -a,  0,  b ),
            glm.vec3(  0, -b, -a ),
            glm.vec3(  a,  0, -b ),
            glm.vec3(  a,  0,  b ),
            glm.vec3( -a,  0, -b ),
            glm.vec3(  b, -a,  0 ),
            glm.vec3( -b, -a,  0 ),
        ]

    @classmethod
    def get_dodecahedron_positions(cls):
        phi = (1. + math.sqrt(5.)) / 2.
        a = 0.5
        b = 0.5 / phi
        c = 0.5 * (2. - phi)

        points = [
            (-a, -c, 0),
            (-a, c, 0),
            (-b, -b, -b),
            (-b, -b, b),
            (-b, b, -b),
            (-b, b, b),
            (-c, 0, -a),
            (-c, 0, a),
            (0, -a, -c),
            (0, -a, c),
            (0, a, -c),
            (0, a, c),
            (c, 0, -a),
            (c, 0, a),
            (b, -b, -b),
            (b, -b, b),
            (b, b, -b),
            (b, b, b),
            (a, -c, 0),
            (a, c, 0),
        ]
        return [glm.vec3(p) for p in points]

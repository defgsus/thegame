import glm

from .TriangleMesh import TriangleMesh
from .LineMesh import LineMesh


class MeshFactory:
    
    @staticmethod
    def add_cube(mesh, size=(1,1,1), origin=(0, 0, 0)):
        r = glm.vec3(size) / 2.
        o = glm.vec3(origin)
        if isinstance(mesh, (TriangleMesh, LineMesh)):
            # front
            mesh.add_quad(o+(-r.x,-r.y,-r.z), o+( r.x,-r.y,-r.z), o+( r.x, r.y,-r.z), o+(-r.x, r.y,-r.z))
            # left
            mesh.add_quad(o+(-r.x,-r.y, r.z), o+(-r.x,-r.y,-r.z), o+(-r.x, r.y,-r.z), o+(-r.x, r.y, r.z))
            # right
            mesh.add_quad(o+( r.x,-r.y,-r.z), o+( r.x,-r.y, r.z), o+( r.x, r.y, r.z), o+( r.x, r.y,-r.z))
            # back
            mesh.add_quad(o+( r.x,-r.y, r.z), o+(-r.x,-r.y, r.z), o+(-r.x, r.y, r.z), o+( r.x, r.y, r.z))
            # top
            mesh.add_quad(o+(-r.x, r.y,-r.z), o+( r.x, r.y,-r.z), o+( r.x, r.y, r.z), o+(-r.x, r.y, r.z))
            # bottom
            mesh.add_quad(o+(-r.x,-r.y, r.z), o+( r.x,-r.y, r.z), o+( r.x,-r.y,-r.z), o+(-r.x,-r.y,-r.z))

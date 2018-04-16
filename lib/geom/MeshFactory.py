import glm

from .TriangleMesh import TriangleMesh
from .LineMesh import LineMesh


class MeshFactory:
    
    @staticmethod
    def add_cube(mesh, size=(1,1,1)):
        r = glm.vec3(size) / 2.
        if isinstance(mesh, TriangleMesh):
            # front
            mesh.add_quad((-r.x,-r.y,-r.z), ( r.x,-r.y,-r.z), ( r.x, r.y,-r.z), (-r.x, r.y,-r.z))
            # left
            mesh.add_quad((-r.x,-r.y, r.z), (-r.x,-r.y,-r.z), (-r.x, r.y,-r.z), (-r.x, r.y, r.z))
            # right
            mesh.add_quad(( r.x,-r.y,-r.z), ( r.x,-r.y, r.z), ( r.x, r.y, r.z), ( r.x, r.y,-r.z))
            # back
            mesh.add_quad(( r.x,-r.y, r.z), (-r.x,-r.y, r.z), (-r.x, r.y, r.z), ( r.x, r.y, r.z))
            # top
            mesh.add_quad((-r.x, r.y,-r.z), ( r.x, r.y,-r.z), ( r.x, r.y, r.z), (-r.x, r.y, r.z))
            # bottom
            mesh.add_quad((-r.x,-r.y, r.z), ( r.x,-r.y, r.z), ( r.x,-r.y,-r.z), (-r.x,-r.y,-r.z))
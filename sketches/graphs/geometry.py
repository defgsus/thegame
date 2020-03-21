import glm

from lib.opengl.core.base import *
from lib.opengl import *
from lib.geom import TriangleMesh, TriangleHashMesh, MeshFactory, Polygons


def make_dodec(factory, mesh, p):
    def add_pentagon(p1, p2, p3, p4, p5):
        mesh.add_triangle(p1, p2, p5)
        mesh.add_triangle(p2, p3, p5)
        mesh.add_triangle(p5, p3, p4)

    factory.add_cube(mesh, origin=p[9], size=(0.2, 0.2, 0.2))

    add_pentagon(p[0], p[1], p[4], p[6], p[2])
    add_pentagon(p[0], p[3], p[7], p[5], p[1])
    add_pentagon(p[3], p[9], p[15], p[13], p[7])
    add_pentagon(p[7], p[13], p[17], p[11], p[5])
    add_pentagon(p[15], p[18], p[19], p[17], p[13])
    add_pentagon(p[18], p[15], p[9], p[8], p[14])
    add_pentagon(p[9], p[18], p[19], p[17], p[13])


def grid_positions(num_x, num_y=None, num_z=None):
    if num_y is None:
        num_y = num_x
    if num_z is None:
        num_z = num_x
    cx = (num_x-1) / -2
    cy = (num_y-1) / -2
    cz = (num_z-1) / -2
    positions = []
    for z in range(num_z):
        for y in range(num_y):
            for x in range(num_x):
                positions.append(glm.vec3(
                    x + cx, y + cy, z + cz
                ))
    return positions


def create_mesh():

    poly = Polygons()
    factory = MeshFactory()

    positions = factory.get_icosahedron_positions()
    positions = grid_positions(6)

    with factory:
        factory.scale(1)
        for pos in factory.get_icosahedron_positions():
            with factory:
                factory.translate(pos*2)
                factory.look(glm.normalize(glm.vec3(pos)), (0, 1, 0))
                factory.rotate_x(90)
                factory.add_cylinder(poly, radius=.1)

        for pos in factory.get_dodecahedron_positions():
            with factory:
                factory.translate(pos*2)
                factory.look(glm.normalize(glm.vec3(pos)), (0, 1, 0))
                factory.rotate_x(90)
                factory.add_cylinder(poly, radius=.02)

    mesh = poly.create_mesh()

    return mesh


class RenderMeshNode(RenderNode):
    def __init__(self, name, mesh):
        super().__init__(name)
        self.mesh = mesh
        self.drawable = self.mesh.create_drawable()
        self.drawable.shader.set_fragment_source(
            DEFAULT_SHADER_VERSION + """
        #line 27
        uniform sampler2D u_tex1;
        uniform sampler2D u_tex2;
        
        in vec4 v_pos;
        in vec4 v_color;
        in vec3 v_normal;
        in vec2 v_texcoord;
        
        uniform float u_time;
        
        out vec4 fragColor;
        
        vec3 lighting(in vec3 pos, in vec3 norm, in vec3 light_pos, in vec3 color) {
            vec3 light_norm = normalize(light_pos - pos);
            float d = max(0., dot(norm, light_norm));
            return color * pow(d, 5.);
        }
        
        void main() {
            //vec3 col = texture(u_tex1, v_texcoord).xyz;
            
            vec3 col = vec3(.15) + .1 * v_normal;
            
            vec3 norm = normalize(v_normal + .1 * sin(length(v_pos.xyz) * 34. - 5. * u_time));
            
            col += .3 * lighting(v_pos.xyz, norm, vec3(3, 0, 1), vec3(1, .6, .4));
            col += .3 * lighting(v_pos.xyz, norm, vec3(-3, 1, 2), vec3(.5, 1, .4));
            col += .3 * lighting(v_pos.xyz, norm, vec3(1, 5, 3), vec3(.3, .6, 1));
            
            fragColor = vec4(col, 1);
        }
        """)

    def num_multi_sample(self):
        return 32

    def has_depth_output(self):
        return True

    def release(self):
        self.drawable.release()

    def render(self, rs, pass_num):
        self.drawable.shader.set_uniform("u_time", rs.time)
        #self.drawable.shader.set_uniform("u_tex1", 0)
        #self.drawable.shader.set_uniform("u_tex2", 1)
        self.drawable.shader.set_uniform("u_projection", rs.projection.matrix)

        #glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)

        self.drawable.draw()


def create_render_graph():
    graph = RenderGraph()
    graph.add_node(RenderMeshNode("geom", create_mesh()))

    return graph

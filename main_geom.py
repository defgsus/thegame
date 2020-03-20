import pyglet

from lib.opengl.core.base import *
from lib.opengl import *
from lib.geom import TriangleMesh, TriangleHashMesh, MeshFactory, Polygons
from lib.world.render import RenderSettings
from lib.world import WorldProjection

from sketches.RenderGraphWindow import RenderGraphWindow as MainWindow


def create_mesh():

    poly = Polygons()
    factory = MeshFactory()

    #factory.add_cube(poly)
    #factory.add_uv_sphere(poly, 1, num_v=6, num_u=12)
    #factory.add_octahedron(poly)
    #factory.add_icosahedron(poly)
    for pos in factory.get_icosahedron_positions():
        with factory:
            factory.translate(pos * 2)
            factory.add_dodecahedron(poly)

    #factory.add_triangle(poly, (0, 0, 0), (1, 0, 0), (1, 1, 0))
    #factory.rotate_x(30)
    #factory.translate((0, 1, 0))
    #factory.add_triangle(poly, (0, 0, 0), (1, 0, 0), (1, 1, 0))

    poly.extrude(1.1)
    #poly.extrude(.1)
#    poly.extrude(.1)

    mesh = poly.create_mesh()

    #mesh = TriangleMesh()
    #MeshFactory.add_cube(mesh)
    #MeshFactory.add_cube(mesh, origin=(0, 1.1, 0))

    #print(mesh.triangles_array())

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

        glDisable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)

        self.drawable.draw()


def create_render_graph():
    graph = RenderGraph()
    graph.add_node(RenderMeshNode("geom", create_mesh()))

    return graph


gl_config = pyglet.gl.Config(
    major_version=3,
    minor_version=0,
    double_buffer=True,
)
main_window = MainWindow(
    render_graph=create_render_graph(),
    render_settings=RenderSettings(1024, 1024, WorldProjection.P_PERSPECTIVE),
    config=gl_config,
    resizable=True,
)

pyglet.app.run()

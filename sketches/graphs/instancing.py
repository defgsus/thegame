import random

import glm

from lib.opengl.core.base import *
from lib.opengl import *
from lib.geom import TriangleMesh, TriangleHashMesh, MeshFactory, Polygons


class InstancingNode(RenderNode):

    def __init__(self, name):
        super().__init__(name)
        factory = MeshFactory()
        self.mesh = TriangleMesh()
        factory.add_cube(self.mesh, 1.)

        self.drawable = self.mesh.create_drawable()
        self.drawable.shader.set_vertex_source(
            DEFAULT_SHADER_VERSION + """
            #line 19
            uniform mat4 u_projection;
            uniform mat4 u_transformation;
            uniform mat4 u_transformation_inv;
            
            in vec4 a_position;
            in vec3 a_normal;
            in vec4 a_color;
            in vec2 a_texcoord;
            in vec3 a_ambient;
            
            in vec4 a_instance_color;
            in mat4 a_instance_transform;
            
            out vec4 v_pos;
            out vec3 v_normal;
            out vec4 v_color;
            out vec2 v_texcoord;
            out vec3 v_ambient;
            out vec3 v_world_normal;
            
            void main()
            {
                vec4 position = a_instance_transform * a_position;
                
                v_pos = position;
                v_normal = a_normal;
                v_world_normal = normalize((vec4(a_normal, 0.) * u_transformation_inv).xyz);
                v_color = a_instance_color;
                v_texcoord = a_texcoord;
                v_ambient = a_ambient;
                gl_Position = u_projection * u_transformation * position;
            }
            """
        )
        self.drawable.shader.set_fragment_source(
            DEFAULT_SHADER_VERSION + """
        #line 18
        
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
            vec3 col = v_color.xyz + .02 * v_normal;
            
            vec3 norm = v_normal; //normalize(v_normal + .1 * sin(length(v_pos.xyz) * 34. - 5. * u_time));
            
            col += .3 * lighting(v_pos.xyz, norm, vec3(3, 0, 1), vec3(1, .6, .4));
            col += .3 * lighting(v_pos.xyz, norm, vec3(-3, 1, 2), vec3(.5, 1, .4));
            col += .3 * lighting(v_pos.xyz, norm, vec3(1, 5, 3), vec3(.3, .6, 1));
            
            fragColor = vec4(col, 1);
        }
        """)
        if 0:
            self.instance_colors = [
                1, 0, 0, 1,
                0, 1, 0, 1,
                0, 0, 1, 1,
                1, 1, 0, 1,
            ]
            self.instance_transforms = [
                glm.mat4(1),
                glm.translate(glm.mat4(1), glm.vec3(1, 0, 0)),
                glm.translate(glm.mat4(1), glm.vec3(1, 1, 0)),
                glm.rotate(glm.translate(glm.mat4(1), glm.vec3(-.5, 1, 0)), glm.pi()/4., glm.vec3(0, 1, 0)),
            ]
        else:
            self.instance_colors = []
            self.instance_transforms = []
            for i in range(500):
                self.instance_colors.append(random.uniform(0.1, 1.))
                self.instance_colors.append(random.uniform(0.1, 1.))
                self.instance_colors.append(random.uniform(0.1, 1.))
                self.instance_colors.append(1.)

                self.instance_transforms.append(
                    glm.translate(
                        glm.mat4(1),
                        20. * glm.vec3(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))
                    )
                )

    def num_multi_sample(self):
        return 32

    def has_depth_output(self):
        return True

    def release(self):
        self.drawable.release()

    def create(self, rs: RenderSettings):
        self.drawable.prepare()
        vao: VertexArrayObject = self.drawable.vao

        vao.create_attribute_buffer(
            attribute_location=self.drawable.shader.attribute("a_instance_color").location,
            num_dimensions=4,
            Type=GLfloat,
            values=self.instance_colors,
            divisor=1,
        )

        flat_transforms = []
        for mat in self.instance_transforms:
            for col in mat:
                for v in col:
                    flat_transforms.append(v)

            for i in range(4):
                vao.create_attribute_buffer(
                    attribute_location=self.drawable.shader.attribute("a_instance_transform").location + i,
                    num_dimensions=4,
                    Type=GLfloat,
                    values=flat_transforms,
                    stride=ctypes.sizeof(GLfloat) * 16,
                    offset=ctypes.sizeof(ctypes.c_float) * 4 * i,
                    divisor=1,
                )

    def render(self, rs, pass_num):
        self.drawable.shader.set_uniform("u_time", rs.time)
        self.drawable.shader.set_uniform("u_projection", rs.projection.matrix)

        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)

        self.drawable.draw(num_instances=len(self.instance_colors))


def create_render_graph():
    graph = RenderGraph()
    graph.add_node(InstancingNode("insti"))

    return graph

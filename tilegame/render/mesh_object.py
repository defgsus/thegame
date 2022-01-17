import math
from typing import Optional, Dict

import glm
import numpy as np

from lib.opengl.core.base import *
from lib.opengl import *
from lib.gen import Worker
from lib.geom import *
from lib.geom.TriangleMesh import vecs_to_list

from .rs import GameRenderSettings
from tests.util import Timer


class MeshObject:

    def __init__(self, num_parts: int = 3, name: str = "mesh"):
        self.name = name
        self.num_parts = num_parts
        self.part_transforms = [glm.mat4(1.) for i in range(self.num_parts)]
        #self.part_transforms[0] *= glm.translate(glm.mat4(1), glm.vec3(-1, 0, 0))
        #self.part_transforms[1] *= glm.translate(glm.mat4(1), glm.vec3(1, 0, 0))
        self.mesh: Optional[TriangleMesh] = None
        self.drawable: Optional[Drawable] = None
        self._create_mesh()
        self.drawable = self.mesh.create_drawable(f"{self.name}-mesh")
        self.drawable.shader.set_vertex_source(
            DEFAULT_SHADER_VERSION + """
            #line 30
            uniform mat4 u_projection;
            uniform mat4 u_transformation;
            uniform mat4 u_transformation_inv;
            uniform mat4[%(num_parts)s] u_part_transformation;
            
            in vec4 a_position;
            in vec3 a_normal;
            in vec4 a_color;
            in vec2 a_texcoord;
            in vec3 a_ambient;
            in float a_part;
            
            out vec4 v_pos;
            out vec3 v_normal;
            out vec4 v_color;
            out vec2 v_texcoord;
            out vec3 v_ambient;
            out vec3 v_world_normal;
            
            void main()
            {
                int part = int(a_part);
                vec4 position = u_part_transformation[part] * a_position;
                
                v_pos = position;
                v_normal = a_normal;
                v_world_normal = normalize((vec4(a_normal, 0.) * u_transformation_inv).xyz);
                v_color = a_color;
                v_texcoord = a_texcoord;
                v_ambient = a_ambient;
                gl_Position = u_projection * u_transformation * position;
            }
            """ % {
                "num_parts": self.num_parts
            }
        )
        self.drawable.shader.set_fragment_source(
            DEFAULT_SHADER_VERSION + """
            #line 63
            uniform sampler2D u_tex1;
            uniform mat4 u_translation;    
            
            in vec4 v_pos;
            in vec4 v_color;
            in vec3 v_normal;
            in vec3 v_world_normal;
            in vec2 v_texcoord;
            
            out vec4 fragColor;
            
            void main() {
                vec4 col = v_color;
                //col += texture(u_tex1, v_texcoord);
                col.xyz = clamp(v_world_normal, 0., 1.);
                fragColor = col;
            }
            """
        )

    def release(self):
        self.drawable.release()

    def render(self, projection: glm.mat4, transformation: glm.mat4):
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)

        transforms = np.array([m.to_list() for m in self.part_transforms], dtype="float32")
        transforms = transforms.flatten()
        self.drawable.shader.set_uniform("u_projection", projection)
        self.drawable.shader.set_uniform("u_transformation", transformation)
        self.drawable.shader.set_uniform("u_transformation_inv", glm.inverse(transformation))
        self.drawable.shader.set_uniform("u_part_transformation[0]", transforms)
        self.drawable.draw()

    def set_movement(self, t: float, amount: float):
        t *= 5
        head = glm.translate(glm.mat4(), glm.vec3(0, 0, 3))
        head = glm.rotate(head, math.sin(t)*(.1+.2*amount), glm.vec3(0, 0, 1))
        self.part_transforms[0] = head

        d = -1
        for i in range(2):
            rest_pos = glm.vec3(.4 * d, 0.1, 0)
            walk_pos = glm.vec3(.4*d, .3*math.sin(t+d*1.57), 0)
            foot = glm.translate(glm.mat4(), glm.mix(rest_pos, walk_pos, amount))
            foot = glm.scale(foot, glm.vec3(.3, .5, .3))
            self.part_transforms[i+1] = foot
            d = 1

    def _create_mesh(self):
        self.mesh = TriangleMesh()
        self.mesh.create_attribute("a_part", 1, 0., gl.GLfloat)
        factory = MeshFactory()

        # head
        self.mesh.set_attribute_value("a_part", 0.)
        factory.add_dodecahedron(self.mesh)
        # left food
        self.mesh.set_attribute_value("a_part", 1.)
        factory.add_dodecahedron(self.mesh)
        # right food
        self.mesh.set_attribute_value("a_part", 2.)
        factory.add_dodecahedron(self.mesh)


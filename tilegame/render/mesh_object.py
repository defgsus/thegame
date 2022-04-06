import math
import ctypes
from typing import Optional, Dict, List

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

    def __init__(self, mesh: TriangleMesh, num_parts: int = 1, name: str = "mesh"):
        self.name = name
        self.num_parts = num_parts
        self.part_transforms = [glm.mat4(1.) for i in range(self.num_parts)]
        self.mesh = mesh
        self.drawable: Optional[Drawable] = None
        self.drawable = self.mesh.create_drawable(f"{self.name}-mesh")
        self.instance_buffers: List[ArrayBufferObject] = []
        self.drawable.shader.set_vertex_source(
            DEFAULT_SHADER_VERSION + """
            #line 28
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
            in mat4 a_instance_transform;
            
            out vec4 v_pos;
            out vec3 v_normal;
            out vec4 v_color;
            out vec2 v_texcoord;
            out vec3 v_ambient;
            out vec3 v_world_normal;
            
            void main()
            {
                int part = int(a_part);
                vec4 position = a_instance_transform * 
                        u_part_transformation[part] * a_position;
                position.x += float(gl_InstanceID);
                
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

    def render(
            self,
            projection: glm.mat4,
            transformation: glm.mat4,
    ):
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)

        transforms = np.array([m.to_list() for m in self.part_transforms], dtype="float32")
        transforms = transforms.flatten()
        self.drawable.shader.set_uniform("u_projection", projection)
        self.drawable.shader.set_uniform("u_transformation", transformation)
        self.drawable.shader.set_uniform("u_transformation_inv", glm.inverse(transformation))
        self.drawable.shader.set_uniform("u_part_transformation[0]", transforms)

        if not self.instance_buffers:
            self.drawable.prepare()
            vao: VertexArrayObject = self.drawable.vao

            mat = glm.mat4(1)
            for i in range(4):
                self.instance_buffers.append(
                    vao.create_attribute_buffer(
                        attribute_location=self.drawable.shader.attribute("a_instance_transform").location + i,
                        num_dimensions=4,
                        Type=GLfloat,
                        #values=[1.,0.,0.,0., 0.,1.,0.,0., 0.,0.,1.,0., 0.,0.,0.,1.],
                        values=mat[i],
                        stride=ctypes.sizeof(GLfloat) * 16,
                        offset=ctypes.sizeof(ctypes.c_float) * 4 * i,
                        divisor=1,
                    )
                )

        self.drawable.draw(num_instances=None)

    def render_multi(
            self,
            projection: glm.mat4,
            transformations: List[glm.mat4],
    ):
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)

        transforms = np.array([m.to_list() for m in self.part_transforms], dtype="float32")
        transforms = transforms.flatten()
        self.drawable.shader.set_uniform("u_projection", projection)
        self.drawable.shader.set_uniform("u_transformation", glm.mat4(1))
        self.drawable.shader.set_uniform("u_transformation_inv", glm.mat4(1))
        self.drawable.shader.set_uniform("u_part_transformation[0]", transforms)

        flat_transforms = []
        for mat in transformations:
            for col in mat:
                for v in col:
                    flat_transforms.append(v)

        if not self.instance_buffers:
            self.drawable.prepare()
            vao: VertexArrayObject = self.drawable.vao

            for i in range(4):
                self.instance_buffers.append(
                    vao.create_attribute_buffer(
                        attribute_location=self.drawable.shader.attribute("a_instance_transform").location + i,
                        num_dimensions=4,
                        Type=GLfloat,
                        values=flat_transforms,#[i*4:],
                        stride=ctypes.sizeof(GLfloat) * 16,
                        offset=ctypes.sizeof(ctypes.c_float) * 4 * i,
                        divisor=1,
                    )
                )

        self.drawable.draw(num_instances=len(transformations))

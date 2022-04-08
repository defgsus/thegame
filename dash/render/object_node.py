from typing import Optional, Dict, Tuple

import glm
import numpy as np

from lib.opengl.core.base import *
from lib.opengl import *
from lib.geom import MeshFactory, TriangleMesh

from .shader_node import GameShaderNode
from .rs import GameRenderSettings
from ..map import ObjectMap


class ObjectNode(GameShaderNode):

    def __init__(
            self,
            name: str,
            object_map: ObjectMap,
    ):
        super().__init__(name)
        self.object_map = object_map
        self.drawable = Drawable(f"{name}-drawable")
        self._element_buffer: ArrayBufferObject = None

        self.drawable.shader.set_vertex_source(DEFAULT_SHADER_VERSION + """
        #include <vector.glsl>
        #line 29
        uniform mat4 u_projection;
        uniform mat4 u_transformation;
        uniform mat4 u_transformation_inv;
        
        in vec4 a_position;
        in vec3 a_normal;
        in vec4 a_color;
        in vec2 a_texcoord;
        in vec3 a_ambient;

        in vec4 a_element_buffer;
        
        out vec4 v_pos;
        out vec3 v_normal;
        out vec4 v_color;
        out vec2 v_texcoord;
        out vec3 v_ambient;
        out vec3 v_world_normal;
        
        void main()
        {
            vec4 position = a_position * a_element_buffer.w;
            position.xy = rotate_z(position.xy, a_element_buffer.z) + a_element_buffer.xy;
            
            v_pos = a_position;
            v_normal = a_normal;
            v_world_normal = normalize((vec4(a_normal, 0.) * u_transformation_inv).xyz);
            v_color = a_color;
            v_texcoord = a_texcoord;
            v_ambient = a_ambient;
            gl_Position = u_projection * u_transformation * position;
        }
        """)

        mesh = TriangleMesh()
        MeshFactory().add_quad(
            mesh,
            glm.vec3(-.5, -.5, 0), glm.vec3(-.5, .5, 0),
            glm.vec3(.5, .5, 0), glm.vec3(.5, -.5, 0)
        )
        mesh.update_drawable(self.drawable)

    def create(self, render_settings: GameRenderSettings):
        super().create(render_settings)

    def release(self):
        self.drawable.release()
        super().release()

    def render(self, rs: GameRenderSettings, pass_num: int):
        self.drawable.shader.set_uniform("u_projection", rs.projection.projection_matrix_4())
        self.drawable.shader.set_uniform("u_transformation", rs.projection.transformation_matrix_4())
        self.drawable.prepare()

        element_buffer_values = []
        for o in self.object_map.objects:
            element_buffer_values.append(o.position.x)
            element_buffer_values.append(o.position.y)
            element_buffer_values.append(o.rotation)
            element_buffer_values.append(o.scale)

        element_buffer_values = np.array(element_buffer_values, dtype="float32")

        vao: VertexArrayObject = self.drawable.vao
        if not self._element_buffer:
            self._element_buffer = vao.create_attribute_buffer(
                attribute_location=self.drawable.shader.attribute("a_element_buffer").location,
                num_dimensions=4,
                Type=GLfloat,
                values=element_buffer_values,
                stride=ctypes.sizeof(GLfloat) * 4,
                offset=0,
                divisor=1,
                storage_type=GL_DYNAMIC_DRAW,
            )
        else:
            self._element_buffer.bind()
            self._element_buffer.upload(GLfloat, element_buffer_values)

        self.drawable.draw(without_prepare=True, num_instances=len(self.object_map.objects))

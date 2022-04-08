from typing import Optional, Dict, Tuple

import glm
import numpy as np

from lib.opengl.core.base import *
from lib.opengl import *
from lib.geom import MeshFactory, TriangleMesh

from .shader_node import GameShaderNode
from .rs import GameRenderSettings
from ..map import Objects


class ObjectsNode(GameShaderNode):

    def __init__(
            self,
            name: str,
            object_map: Objects,
            tile_size: Tuple[int, int],
            tile_set_size: Tuple[int, int],
    ):
        super().__init__(name)
        self.object_map = object_map
        self.tile_size = tile_size
        self.tile_set_size = tile_set_size

        self.drawable = Drawable(f"{name}-drawable")
        self._element_buffer: Optional[ArrayBufferObject] = None
        self._element_texture: Optional[ArrayBufferObject] = None

        self.drawable.shader.set_vertex_source(DEFAULT_SHADER_VERSION + """
        #include <vector.glsl>
        #line 35
        uniform mat4 u_projection;
        uniform mat4 u_transformation;
        uniform mat4 u_transformation_inv;
        uniform ivec2 u_tile_size;
        uniform ivec2 u_tile_set_size;

        in vec4 a_position;
        in vec2 a_texcoord;
        in vec3 a_ambient;

        in vec4 a_element_buffer;
        in vec4 a_element_texture;
        
        out vec4 v_pos;
        out vec2 v_texcoord;
        
        void main()
        {
            vec4 position = a_position;
            position.xy *= a_element_buffer.w;
            position.xy = rotate_z(position.xy, a_element_buffer.z) + a_element_buffer.xy;
            
            int tile_idx = int(a_element_texture.w + .1);
            v_texcoord = a_texcoord / u_tile_set_size 
                + vec2(tile_idx % u_tile_set_size.x, tile_idx / u_tile_set_size.x) / u_tile_set_size;
            
            v_pos = a_position;
            //v_world_normal = normalize((vec4(a_normal, 0.) * u_transformation_inv).xyz);
            
            gl_Position = u_projection * u_transformation * position;
        }
        """)

        self.drawable.shader.set_fragment_source(DEFAULT_SHADER_VERSION + """
        #line 77
        uniform sampler2D u_tex1;
        
        in vec4 v_pos;
        in vec2 v_texcoord;
        
        out vec4 fragColor;
        
        void main() {
            vec4 col = texture(u_tex1, v_texcoord);
            //col.xyz += v_normal*.3;
            fragColor = col;
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
        self.drawable.shader.set_uniform("u_tile_size", self.tile_size)
        self.drawable.shader.set_uniform("u_tile_set_size", self.tile_set_size)
        self.drawable.prepare()

        element_buffer_values = []
        element_texture_values = []
        for o in self.object_map.objects:
            if rs.is_object_visible(o.position, o.scale):
                element_buffer_values.append(o.position.x)
                element_buffer_values.append(o.position.y)
                element_buffer_values.append(o.rotation)
                element_buffer_values.append(o.scale)
                element_texture_values.append(1)
                element_texture_values.append(1)
                element_texture_values.append(1)
                element_texture_values.append(o.texture_idx)

        if not element_texture_values:
            return

        element_buffer_values = np.array(element_buffer_values, dtype="float32")
        element_texture_values = np.array(element_texture_values, dtype="float32")

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
            if self.drawable.shader.has_attribute("a_element_texture"):
                self._element_texture = vao.create_attribute_buffer(
                    attribute_location=self.drawable.shader.attribute("a_element_texture").location,
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
            if self._element_texture:
                self._element_texture.bind()
                self._element_texture.upload(GLint, element_texture_values)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.drawable.draw(without_prepare=True, num_instances=len(self.object_map.objects))

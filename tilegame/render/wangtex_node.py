from functools import partial
from typing import Optional, Dict

import glm
import numpy as np

from lib.opengl.core.base import *
from lib.opengl import *
from lib.gen import Worker

from .shader_node import GameShaderNode
from .rs import GameRenderSettings
from ..map import TilemapSampler
from tests.util import Timer


class WangTextureNode(GameShaderNode):

    def __init__(self, name: str):
        super().__init__(name)
        self.map_texture = Texture2D()
        self.map_uploaded = False

    def get_game_shader_code(self):
        return """
        #include <wang-tile.glsl>
        #line 26
        
        uniform ivec2 u_tile_set_size;
        
        vec3 wang_tile(in vec2 uv, int idx) {
            float d = wang_tile_distance(uv, idx);
            
            vec3 col1 = vec3(0.2, .5, .7);
            vec3 col2 = vec3(0.8, 0.6, 0.2);
            vec3 col = mix(col1, col2, smoothstep(0.05, -0.05, d));
            return col;
        }
                    
        vec4 game_shader(in GameShader gs) {
            vec2 map_pos = gs.texCoord * u_tile_set_size;
            ivec2 map_pos_i = ivec2(map_pos);
            ivec4 map = ivec4(texelFetch(u_tex4, map_pos_i, 0));            
            vec2 tile_pos = fract(map_pos);
            
            vec4 color = vec4(wang_tile(tile_pos * 2. - 1., map.z), 1);
            
            return color;
        }
        """

    def num_multi_sample(self) -> int:
        return 32

    def create(self, render_settings: RenderSettings):
        super().create(render_settings)
        if not self.map_texture.is_created():
            self.map_texture.create()

    def release(self):
        self.map_texture.release()
        super().release()

    def render(self, rs: GameRenderSettings, pass_num: int):
        self.map_texture.set_active_texture(3)
        self.map_texture.bind()
        self.map_texture.set_parameter(gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        self.update_map(rs)

        self.quad.drawable.shader.set_uniform("u_tile_set_size", [16, 16])
        super().render(rs, pass_num)

    def update_map(self, rs: GameRenderSettings):
        if not self.map_uploaded:
            array = np.arange(0, 256).reshape([16, 16, 1]).repeat(3, axis=2)
            self.upload_map(array)

    def upload_map(self, float_array: np.ndarray):
        # print(float_array)
        if float_array.dtype.name != "float32":
            float_array = float_array.astype("float32")
        if not self.map_texture.is_created():
            self.map_texture.create()
        self.map_texture.bind()
        self.map_texture.upload_numpy(
            float_array,
            width=float_array.shape[1],
            input_format=gl.GL_RGB, gpu_format=gl.GL_RGB32F,
        )

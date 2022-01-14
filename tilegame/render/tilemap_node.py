from typing import Optional, Dict

import glm
import numpy as np

from lib.opengl.core.base import *
from lib.opengl import *

from .shader_node import GameShaderNode
from .rs import GameRenderSettings


class TileMapNode(GameShaderNode):

    def __init__(self, name: str):
        super().__init__(name)
        self.map_texture = Texture2D()

    def get_game_shader_code(self):
        return """
        #line 21
        uniform ivec2 u_tile_size;
        uniform ivec2 u_tile_set_size;
        
        vec4 game_shader(in GameShader gs) {
            ivec2 map_pos = ivec2(gs.map_pos);
            map_pos.y = 20 - map_pos.y;
            ivec4 map = ivec4(texelFetch(u_tex4, map_pos, 0));
            
            vec2 tile_pos = fract(gs.map_pos);
            
            // when using bilinear mag filter, this is needed 
            //tile_pos = tile_pos * (float(u_tile_size - 1.) + .5) / float(u_tile_size);
            
            //int tile_idx = int(map_pos.y + map_pos.x) % (u_tile_set_size.x * u_tile_set_size.y);
            int tile_idx = map.x;
            tile_pos += vec2(tile_idx % u_tile_set_size.x, (tile_idx / u_tile_set_size.x));
               
            vec4 color = texture(u_tex1, tile_pos / u_tile_set_size);
            
            float frame = smoothstep(0.1, 0., max(abs(gs.uv.x), abs(gs.uv.y)) - 1.);
            color *= .5 + .5 * frame;
            return color;
        }
        """

    #def num_multi_sample(self) -> int:
    #    return 32

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
        self.quad.drawable.shader.set_uniform("u_tile_size", [32, 32])
        self.quad.drawable.shader.set_uniform("u_tile_set_size", [4, 4])
        super().render(rs, pass_num)

    def upload_map(self, float_array: np.ndarray):
        assert float_array.dtype.name == "float32"
        if not self.map_texture.is_created():
            self.map_texture.create()
        self.map_texture.bind()
        self.map_texture.upload_numpy(
            float_array,
            input_format=gl.GL_RED, gpu_format=gl.GL_R32F,
        )

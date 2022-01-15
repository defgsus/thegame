from typing import Optional, Dict

import glm
import numpy as np

from lib.opengl.core.base import *
from lib.opengl import *

from .shader_node import GameShaderNode
from .rs import GameRenderSettings
from ..map import TileMap


class TileMapNode(GameShaderNode):

    def __init__(self, map: TileMap, name: str):
        super().__init__(name)
        self.map = map
        self.map_texture = Texture2D()
        self.last_map_center = None
        self.last_map_offset = None

    def get_game_shader_code(self):
        return """
        #line 21
        uniform ivec2 u_tile_size;
        uniform ivec2 u_tile_set_size;
                
        vec4 game_shader(in GameShader gs) {
            ivec2 map_pos = ivec2(gs.map_pos);
            //map_pos.y = 20 - map_pos.y;
            ivec4 map = ivec4(texelFetch(u_tex4, map_pos, 0));
            
            vec2 tile_pos = fract(gs.map_pos);
            
            // when using bilinear mag filter, this is needed 
            //tile_pos = tile_pos * (float(u_tile_size - 1.) + .5) / float(u_tile_size);
            
            //int tile_idx = int(map_pos.y + map_pos.x) % (u_tile_set_size.x * u_tile_set_size.y);
            int tile_idx = map.x;
            tile_pos += vec2(tile_idx % u_tile_set_size.x, (tile_idx / u_tile_set_size.x));
               
            vec4 color = texture(u_tex1, tile_pos / u_tile_set_size);
            
            float frame = smoothstep(0.6, 0., max(abs(gs.uv.x), abs(gs.uv.y)) - 1.);
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
        self.update_map(rs)
        self.quad.drawable.shader.set_uniform("u_tile_size", [32, 32])
        self.quad.drawable.shader.set_uniform("u_tile_set_size", [4, 4])
        with rs.projection:
            rs.projection.location = rs.projection.location - self.last_map_offset
            super().render(rs, pass_num)

    def update_map(self, rs: GameRenderSettings):
        map_center = (int(rs.projection.location[0]), int(rs.projection.location[1]))
        if self.last_map_center is None:
            do_update = True
        else:
            dist = abs(self.last_map_center[0] - map_center[0]) + abs(self.last_map_center[1] - map_center[1])
            do_update = dist > 2

        if do_update:
            w, h = 16, 16  # radius
            map_array = self.map.get_map(map_center[0] - w, map_center[1] + h, w * 2 + 1, h * 2 + 1)
            self.upload_map(map_array)
            self.last_map_center = map_center
            self.last_map_offset = glm.vec2(*map_center) - glm.vec2(w, h)

    def upload_map(self, float_array: np.ndarray):
        assert float_array.dtype.name == "float32"
        if not self.map_texture.is_created():
            self.map_texture.create()
        self.map_texture.bind()
        self.map_texture.upload_numpy(
            float_array,
            width=float_array.shape[-1],
            input_format=gl.GL_RED, gpu_format=gl.GL_R32F,
        )

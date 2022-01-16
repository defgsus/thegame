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


class TileMapNode(GameShaderNode):

    def __init__(self, map: TilemapSampler, name: str):
        super().__init__(name)
        self.map = map
        self.map_texture = Texture2D()
        self.last_map_center = None
        self.last_map_offset = None
        self.last_map_scale = None
        self.map_worker = Worker.instance("numpy")
        self.map_requested = False

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
            color.xyz *= .2 + .8 * clamp(map.x/20., 0, 1);
                        
            float frame = smoothstep(0.6, 0., max(abs(gs.uv.x), abs(gs.uv.y)) - 1.);
            color *= .5 + .5 * frame;
            return color;
        }
        """

    def num_multi_sample(self) -> int:
        return 4

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
        if self.last_map_offset:
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
            do_update |= self.last_map_scale * 1.1 < rs.projection.scale

        if do_update or self.map_requested:
            if self.map_requested:
                map_array = None
                result = self.map_worker.pop_result("map")
                if result:
                    self.map_requested = False
                    map_array = result["result"]
                    w, h, map_center, scale = result["extra"]
            else:
                # radius
                w = h = max(16, int(rs.projection.scale * 1.3))
                mx, my, mw, mh = map_center[0] - w, map_center[1] - h, w * 2 + 1, h * 2 + 1
                self.map_worker.request(
                    "map",
                    partial(self.map, mx, my, mw, mh),
                    extra=(w, h, map_center, rs.projection.scale)
                )
                map_array = None
                self.map_requested = True

            if map_array is not None:
                self.upload_map(map_array)
                self.last_map_center = map_center
                self.last_map_offset = glm.vec2(*map_center) - glm.vec2(w, h)
                self.last_map_scale = scale

    def upload_map(self, float_array: np.ndarray):
        if float_array.dtype.name != "float32":
            float_array = float_array.astype("float32")
        if not self.map_texture.is_created():
            self.map_texture.create()
        self.map_texture.bind()
        self.map_texture.upload_numpy(
            float_array,
            width=float_array.shape[-1],
            input_format=gl.GL_RED, gpu_format=gl.GL_R32F,
        )

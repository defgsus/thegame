from typing import Optional, Dict, Tuple

import glm
import numpy as np

from lib.opengl.core.base import *
from lib.opengl import *

from .shader_node import GameShaderNode
from .rs import GameRenderSettings
from ..map import TileMap
from tests.util import Timer


class TileMapNode(GameShaderNode):

    def __init__(
            self,
            name: str,
            map: TileMap,
            tile_size: Tuple[int, int],
            tile_set_size: Tuple[int, int],
    ):
        super().__init__(name)
        self.map = map
        self.map_texture = Texture2D()
        self.tile_size = tile_size
        self.tile_set_size = tile_set_size
        self.last_map_center = None
        self.last_map_offset = None
        self.last_map_scale = None
        self.last_map_state_id = None

    def get_game_shader_code(self):
        return """
        #line 36
        uniform ivec2 u_tile_size;
        uniform ivec2 u_tile_set_size;
        
        vec4 render_tile(in GameShader gs, in vec4 tile, in ivec2 map_offset) {
            ivec2 map_pos = ivec2(gs.map_pos) + map_offset;
            int tile_idx = int(tile.x);
            vec2 offset = tile.yz;
            if (map_offset.x < 0)
                offset.x = -1. + offset.x;
            if (map_offset.y < 0)
                offset.y = -1. + offset.y;
            
            vec2 tile_pos = fract(gs.map_pos);
            
            // when using bilinear mag filter, this is needed 
            //tile_pos = tile_pos * (float(u_tile_size - 2.) + 1.) / float(u_tile_size);
            
            tile_pos -= offset;
            
            vec2 tile_tex_pos = tile_pos + vec2(tile_idx % u_tile_set_size.x, tile_idx / u_tile_set_size.x);
            vec4 color = texture(u_tex1, tile_tex_pos / u_tile_set_size);
            vec2 r = .1 / u_tile_size;
            color = mix(color, vec4(0), smoothstep(r.x, -r.x, tile_pos.x));
            color = mix(color, vec4(0), smoothstep(r.y, -r.y, tile_pos.y));
            color = mix(color, vec4(0), smoothstep(1.-r.x, 1.+r.x, tile_pos.x));
            color = mix(color, vec4(0), smoothstep(1.-r.x, 1.+r.x, tile_pos.y));
            return color;
        }
        
        vec4 game_shader(in GameShader gs) {
            //return texture(u_tex4, gs.texCoord) / 10.;
            ivec2 map_pos = ivec2(gs.map_pos);
            vec4 map00 = vec4(texelFetch(u_tex4, map_pos, 0));
            vec4 map10 = vec4(texelFetch(u_tex4, map_pos - ivec2(1, 0), 0));
            vec4 map01 = vec4(texelFetch(u_tex4, map_pos - ivec2(0, 1), 0));
            vec4 map11 = vec4(texelFetch(u_tex4, map_pos - ivec2(1, 1), 0));
            
            vec4 color = render_tile(gs, map00, ivec2(0, 0));
            if (true) {
                vec4 color2 = render_tile(gs, map10, ivec2(-1, 0));
                color = mix(color, color2, color2.a);
                color2 = render_tile(gs, map01, ivec2(0, -1));
                color = mix(color, color2, color2.a);
                color2 = render_tile(gs, map11, ivec2(-1, -1));
                color = mix(color, color2, color2.a);
            }
                             
            //float frame = smoothstep(0.6, 0., max(abs(gs.uv.x), abs(gs.uv.y)) - 1.);
            vec2 screen_uv = gs.texCoord * 2. - 1.;
            //float frame = smoothstep(1., .8, max(abs(screen_uv.x), abs(screen_uv.y)));
            float frame = 1. - dot(screen_uv*.8, screen_uv);
            color.xyz *= .7 + .3 * frame;
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

        self.quad.drawable.shader.set_uniform("u_tile_size", self.tile_size)
        self.quad.drawable.shader.set_uniform("u_tile_set_size", self.tile_set_size)
        if self.last_map_offset:
            with rs.projection:
                rs.projection.location = rs.projection.location - self.last_map_offset
                super().render(rs, pass_num)

    def update_map(self, rs: GameRenderSettings):
        map_center = (int(rs.projection.location[0]), int(rs.projection.location[1]))
        if self.last_map_center is None or self.map.state_id != self.last_map_state_id:
            do_update = True
        else:
            dist = abs(self.last_map_center[0] - map_center[0]) + abs(self.last_map_center[1] - map_center[1])
            do_update = dist > 2
            do_update |= self.last_map_scale * 1.1 < rs.projection.scale

        if do_update:
            # radius
            w = h = max(16, int(rs.projection.scale * 1.3))
            mx, my, mw, mh = map_center[0] - w, map_center[1] - h, w * 2 + 1, h * 2 + 1

            map_array = self.map.get_window(mx, my, mw, mh)
            self.upload_map(map_array)
            self.last_map_center = map_center
            self.last_map_offset = glm.vec2(*map_center) - glm.vec2(w, h)
            self.last_map_scale = rs.projection.scale
            self.last_map_state_id = self.map.state_id

    def upload_map(self, float_array: np.ndarray):
        float_array = np.ascontiguousarray(float_array)
        if float_array.dtype.name != "float32":
            float_array = float_array.astype("float32")

        if not self.map_texture.is_created():
            self.map_texture.create()
        self.map_texture.bind()
        self.map_texture.upload_numpy(
            float_array,
            width=float_array.shape[1],
            input_format=gl.GL_RGBA, gpu_format=gl.GL_RGBA32F,
        )

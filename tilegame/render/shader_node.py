from typing import Optional, Dict

import glm
import numpy as np

from lib.opengl.core.base import *
from lib.opengl import *
from lib.opengl.postproc import PostProcNode

from .rs import GameRenderSettings


class GameShaderNode(PostProcNode):
    def __init__(self, name: str):
        super().__init__(name)

    def get_game_shader_code(self):
        return """
        #line 19
        vec4 game_shader(in GameShader gs) {
            vec2 auv = abs(gs.uv);
            vec3 col = vec3(
                smoothstep(.01, .0, min(auv.x, auv.y)),
                auv.x, 
                max(
                    auv.y,
                    smoothstep(.01, .0, abs(max(auv.x, auv.y) - 1.))
                )
            );
            ivec2 map_pos = ivec2(gs.map_pos); 
            float checker = abs(map_pos.x + map_pos.y) % 2;
            col *= .7 + .3 * checker;
            return vec4(col, 1);        
        }
        """

    def get_code(self):
        return """
        #line 39
        uniform mat3 u_camera;
        
        struct GameShader {
            vec2 fragCoord;
            vec2 texCoord;
            vec2 uv;
            vec2 map_pos;
        };
        
        vec2 rotate(in vec2 v, in float degree) {
            float sa = sin(degree), ca = cos(degree);
            return vec2(
                v.x * ca - v.y * sa,
                v.x * sa + v.y * ca
            );
        }
        
        _GaMeShAdEr_
        #line 42
        
        void mainImage(out vec4 fragColor, in vec2 fragCoord, in vec2 texCoord) {
            /* TODO: this should be the projection matrix
                and calculation should go to the vertex shader */
            vec2 uv = texCoord;
            uv.x *= u_resolution.x / u_resolution.y;
            uv.x -= .5 * (u_resolution.x - u_resolution.y) / u_resolution.y;    
            uv = uv * 2. - 1.;
            
            vec2 map_pos_f = (u_camera * vec3(uv, 1)).xy;
            
            GameShader gs = GameShader(fragCoord, texCoord, uv, map_pos_f);
            fragColor = game_shader(gs);            
        }   
        """.replace("_GaMeShAdEr_", self.get_game_shader_code())

    def num_multi_sample(self) -> int:
        return 32

    def has_depth_output(self) -> bool:
        return False

    def create(self, render_settings: RenderSettings):
        super().create(render_settings)

    def release(self):
        super().release()

    def render(self, rs: GameRenderSettings, pass_num: int):
        self.quad.drawable.shader.set_uniform("u_camera", rs.projection.transformation_matrix())
        super().render(rs, pass_num)

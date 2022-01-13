from pathlib import Path
from typing import Optional, Dict

import glm
import numpy as np
import scipy.signal

from lib.opengl.core.base import *
from lib.opengl import *
from lib.opengl.postproc import PostProcNode
from lib.geom import TriangleMesh, TriangleHashMesh, MeshFactory, Polygons
from lib.world import Tileset
from lib.ai.automaton import ClassicAutomaton

ASSET_PATH = Path(__file__).resolve().parent.parent.parent / "assets"


def create_render_settings() -> RenderSettings:
    return RenderSettings(
        640, 400,
        #mag_filter=gl.GL_NEAREST,
    )


class WangEdge2:
    TOP = 1
    RIGHT = 2
    BOTTOM = 4
    LEFT = 8

    STRINGS = {
        TOP: "T",
        RIGHT: "R",
        BOTTOM: "B",
        LEFT: "L",
    }

    # (y, x)
    OFFSET = {
        TOP: (-1, 0),
        RIGHT: (0, 1),
        BOTTOM: (1, 0),
        LEFT: (0, -1),
    }

    IDX_TO_TILE = {
        0: 0,
        TOP: 4,
        RIGHT: 1,
        BOTTOM: 12,
        LEFT: 3,
        TOP | RIGHT: 5,
        TOP | LEFT: 7,
        BOTTOM | RIGHT: 13,
        BOTTOM | LEFT: 15,
        TOP | BOTTOM: 8,
        LEFT | RIGHT: 2,
        LEFT | BOTTOM | RIGHT: 14,
        LEFT | TOP | RIGHT: 6,
        TOP | BOTTOM | RIGHT: 9,
        TOP | BOTTOM | LEFT: 11,
        TOP | RIGHT | BOTTOM | LEFT: 10,
    }

    @classmethod
    def tile_idx_to_string(cls, tile: int) -> str:
        s = []
        for key, name in cls.STRINGS.items():
            if tile & key:
                s.append(name)
        return ",".join(s)

    @classmethod
    def get_tile_map(cls, map: np.ndarray) -> np.ndarray:
        h, w = map.shape
        tmap = np.ndarray(map.shape, dtype="int32")
        tmap.fill(cls.IDX_TO_TILE[0])
        for y in range(h):
            for x in range(w):

                if map[y][x]:
                    tile_idx = cls.TOP | cls.RIGHT | cls.BOTTOM | cls.LEFT
                else:
                    tile_idx = 0
                    for key, offset in cls.OFFSET.items():
                        my = y + offset[0]
                        mx = x + offset[1]
                        if my >= h:
                            my = h - my
                        if mx >= w:
                            mx = w - mx
                        tile_idx |= key * int(map[my][mx])

                # print(x, y, cls.tile_idx_to_string(tile_idx))
                if tile_idx in cls.IDX_TO_TILE:
                    tmap[y][x] = cls.IDX_TO_TILE[tile_idx]

        return tmap


class Map:

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.binary_map: np.ndarray = np.zeros([self.height, self.width])

    def tile_map(self) -> np.ndarray:
        return WangEdge2.get_tile_map(self.binary_map)

    def init_random(self, probability: float = .5):
        self.binary_map = (
            np.random.random([self.height, self.width]) + probability
        ).astype(int)

    def init_automaton(self, preset: Optional[dict] = None):
        preset = dict() if preset is None else preset
        a = ClassicAutomaton(
            width=self.width,
            height=self.height,
            born=preset.get("born") or {1, 2, 3},
            survive=preset.get("survive") or {6},
        )
        a.init_random(preset.get("probability") or .3)
        for i in range(preset.get("iterations") or 100):
            a.step()

        a.born = set()
        a.survive = {3, 4, 5, 6, 7, 8}

        for i in range(1):
            a.step()

        self.binary_map = a.cells


class TiledMapNode(PostProcNode):
    def __init__(self, map: Map, name: str = "tiled"):
        super().__init__(name)
        self.map = map
        self.map_texture = Texture2D()

    def get_code(self):
        return """
        #line 142
        const ivec2 tile_size = ivec2(32, 32);
        const ivec2 tile_map_size = ivec2(4, 4);
        
        vec2 rotate(in vec2 v, in float degree) {
            float sa = sin(degree), ca = cos(degree);
            return vec2(
                v.x * ca - v.y * sa,
                v.x * sa + v.y * ca
            );
        }
        
        //vec4 tile_texture(int tile_idx, 
        void mainImage(out vec4 fragColor, in vec2 fragCoord, in vec2 texCoord) {
            vec2 uv = (fragCoord / u_resolution.y);
            uv.x -= .5 * u_resolution.y / u_resolution.x;    
            
            vec2 map_pos_f = uv;
            map_pos_f = rotate(map_pos_f - .5, sin(u_time)*0.02) + .5;
            map_pos_f *= 10. + 5. * sin(u_time/3.);
            map_pos_f.y -= u_time * .9;
            
            ivec2 map_pos = ivec2(map_pos_f);
            map_pos.y = 20 - map_pos.y;
            ivec4 map = ivec4(texelFetch(u_tex4, map_pos, 0));
            
            vec2 tile_pos = fract(map_pos_f);
            
            // when using bilinear mag filter, this is needed 
            //tile_pos = tile_pos * (float(tile_size - 1.) + .5) / float(tile_size);
            
            //int tile_idx = int(map_pos.y + map_pos.x) % (tile_map_size.x * tile_map_size.y);
            int tile_idx = map.x;
            tile_pos += vec2(tile_idx % tile_map_size.x, (tile_idx / tile_map_size.x));
               
            fragColor = texture(u_tex1, tile_pos / tile_map_size);
            //fragColor = texture(u_tex2, uv);            
            
            if (uv.x < 0. || uv.x > 1. || uv.y < 0. || uv.y > 1.)
                fragColor.xyz *= 0.1;
        }   
        """

    def num_multi_sample(self) -> int:
        return 32

    def has_depth_output(self) -> bool:
        return False

    def create(self, render_settings: RenderSettings):
        super().create(render_settings)

        self.map_texture.create()
        self.map_texture.bind()
        self.map_texture.upload_numpy(
            self.map.tile_map().astype("float32"),
            width=self.map.width, input_format=gl.GL_RED, gpu_format=gl.GL_R32F,
        )

    def release(self):
        super().release()
        self.map_texture.release()

    def render(self, rs: RenderSettings, pass_num: int):
        self.map_texture.set_active_texture(3)
        self.map_texture.bind()
        self.map_texture.set_parameter(gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        super().render(rs, pass_num)


def create_render_graph():
    graph = RenderGraph()
    tile_tex = graph.add_node(Texture2DNode(
        ASSET_PATH / "cr31" /
        #"wang2e.png"
        #"border.png"
        #"quad.png"
        "octal.png"
        #"pipe1.png"
        #"mininicular.png"
    ))

    map = Map(128, 128)
    map.init_automaton()
    print(map.tile_map())
    renderer = graph.add_node(TiledMapNode(map))
    graph.connect(tile_tex, 0, renderer, mag_filter=gl.GL_NEAREST)
    return graph


if __name__ == "__main__":

    map = np.array([
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0],
        [0, 0, 1, 1, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ], dtype=int)

    print(map, "\n")

    print(WangEdge2.get_tile_map(map))
    #print(np.convolve(map.map.flatten(), conv_mask.flatten()).reshape([5, 5]))

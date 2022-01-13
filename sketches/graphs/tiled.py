from pathlib import Path

import glm
import numpy as np
import scipy.signal

from lib.opengl.core.base import *
from lib.opengl import *
from lib.opengl.postproc import PostProcNode
from lib.geom import TriangleMesh, TriangleHashMesh, MeshFactory, Polygons
from lib.world import Tileset

ASSET_PATH = Path(__file__).resolve().parent.parent.parent / "assets"


def create_render_settings() -> RenderSettings:
    return RenderSettings(
        640, 400,
        mag_filter=gl.GL_NEAREST,
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
                        tile_idx |= key * map[my][mx]

                # print(x, y, cls.tile_idx_to_string(tile_idx))
                if tile_idx in cls.IDX_TO_TILE:
                    tmap[y][x] = cls.IDX_TO_TILE[tile_idx]

        return tmap


class Map:

    def __init__(self, width: int, height: int, probability: float = .3):
        self.width = width
        self.height = height
        self.binary_map: np.ndarray = (
            np.random.random([height, width]) + probability
        ).astype(int)
        self.map = WangEdge2.get_tile_map(self.binary_map)


class TiledBitmapNode(PostProcNode):
    def __init__(self, name: str):
        super().__init__(name)

    def num_multi_sample(self) -> int:
        return 0

    def get_code(self):
        return """
        #line 113
        const ivec2 tile_size = ivec2(32, 32);
        const ivec2 tile_map_size = ivec2(4, 4);
        
        //vec4 tile_texture(int tile_idx, 
        void mainImage(out vec4 fragColor, in vec2 fragCoord, in vec2 texCoord) {
            vec2 uv = (fragCoord / u_resolution.y);
            uv.x -= .5 * u_resolution.y / u_resolution.x;    
            
            vec2 map_pos_f = 10. * (uv);// * vec2(1, -1) + vec2(0, 1));
            ivec2 map_pos = ivec2(map_pos_f);
            map_pos.y = 10 - map_pos.y;
            ivec4 map = ivec4(texelFetch(u_tex2, map_pos, 0));
            
            vec2 tile_pos = (fract(map_pos_f) * (float(tile_size - 1)) + .5) / float(tile_size);
            
            //int tile_idx = int(map_pos.y + map_pos.x) % (tile_map_size.x * tile_map_size.y);
            int tile_idx = map.x;
            tile_pos += vec2(tile_idx % tile_map_size.x, (tile_idx / tile_map_size.x));
               
            fragColor = texture(u_tex1, tile_pos / tile_map_size);
            //fragColor = texture(u_tex2, uv);            
            
            if (uv.x < 0. || uv.x > 1. || uv.y < 0. || uv.y > 1.)
                fragColor.xyz *= 0.1;
        }   
        """

    def num_multi_sample(self):
        return 0

    def has_depth_output(self):
        return False


MAP = [
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 1, 1, 0, 0, 0, 1,
    1, 0, 1, 0, 1, 0, 0, 1,
    1, 0, 1, 1, 0, 0, 0, 1,
    1, 0, 1, 0, 0, 0, 0, 1,
    1, 0, 1, 0, 0, 0, 0, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
]
def create_render_graph():
    graph = RenderGraph()
    tile_tex = graph.add_node(Texture2DNode(
        ASSET_PATH / "cr31" /
        #"wang2e.png"
        #"border.png"
        "pipe1.png"
        #"mininicular.png"
    ))
    map = Map(8, 8)

    map_tex = graph.add_node(Texture2DNode(
        callback=lambda rs, tex: tex.upload_numpy(
            map.map.astype("float32"),
            map.width, gl.GL_RED, gpu_format=gl.GL_R32F,
        )
    ))
    print(map.map)

    renderer = graph.add_node(TiledBitmapNode("tiled"))
    graph.connect(tile_tex, 0, renderer, mag_filter=gl.GL_NEAREST)
    graph.connect(map_tex, 0, renderer, 1, mag_filter=gl.GL_NEAREST)
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

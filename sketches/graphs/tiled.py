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
        640, 480,
        mag_filter=gl.GL_NEAREST,
    )

class Tiles:
    TOP_LEFT = 1
    TOP = 2
    TOP_RIGHT = 4
    RIGHT = 8
    BOTTOM_RIGHT = 16
    BOTTOM = 32
    BOTTOM_LEFT = 64
    LEFT = 128

    STRINGS = {
        TOP_LEFT: "TL",
        TOP: "T",
        TOP_RIGHT: "TR",
        RIGHT: "R",
        BOTTOM_RIGHT: "BR",
        BOTTOM: "B",
        BOTTOM_LEFT: "BL",
        LEFT: "L",
    }

    # (y, x)
    OFFSET = {
        TOP_LEFT: (-1, -1),
        TOP: (-1, 0),
        TOP_RIGHT: (-1, 1),
        RIGHT: (0, 1),
        BOTTOM_RIGHT: (1, 1),
        BOTTOM: (1, 0),
        BOTTOM_LEFT: (1, -1),
        LEFT: (0, -1),
    }

    TILES = {
        0: 1,
        TOP_LEFT | TOP | TOP_RIGHT | RIGHT | BOTTOM_RIGHT | BOTTOM | BOTTOM_LEFT | LEFT: 0,
        TOP_LEFT |       TOP_RIGHT | RIGHT | BOTTOM_RIGHT | BOTTOM | BOTTOM_LEFT | LEFT: 2,
        TOP_LEFT | TOP | TOP_RIGHT | RIGHT | BOTTOM_RIGHT | BOTTOM | BOTTOM_LEFT       : 16,
        TOP_LEFT | TOP | TOP_RIGHT |         BOTTOM_RIGHT | BOTTOM | BOTTOM_LEFT | LEFT: 17,
        TOP_LEFT | TOP | TOP_RIGHT                                                     : 48,
                                             BOTTOM_RIGHT | BOTTOM | BOTTOM_LEFT | LEFT: 50,

#                                     RIGHT | BOTTOM_RIGHT | BOTTOM                     : 10,
                         TOP_RIGHT | RIGHT | BOTTOM_RIGHT | BOTTOM | BOTTOM_LEFT       : 10,
        TOP_LEFT |                           BOTTOM_RIGHT | BOTTOM | BOTTOM_LEFT | LEFT: 11,
        TOP_LEFT | TOP | TOP_RIGHT | RIGHT | BOTTOM_RIGHT                              : 18,
        TOP_LEFT | TOP | TOP_RIGHT |                                 BOTTOM_LEFT | LEFT: 19,
    }

    TILES_REV = {
        value: key
        for key, value in TILES.items()
    }

    @classmethod
    def tile_to_string(cls, tile: int) -> str:
        s = []
        for key, name in cls.STRINGS.items():
            if tile & key:
                s.append(name)
        return ",".join(s)

    @classmethod
    def get_tile_map(cls, map: np.ndarray) -> np.ndarray:
        h, w = map.shape
        tmap = np.ndarray(map.shape, dtype=int)
        tmap.fill(cls.TILES[0])
        for y in range(h):
            for x in range(w):

                if map[y][x]:
                    tile = cls.TOP_LEFT | cls.TOP | cls.TOP_RIGHT | cls.RIGHT | cls.BOTTOM_RIGHT \
                           | cls.BOTTOM | cls.BOTTOM_LEFT | cls.LEFT
                else:
                    tile = 0
                    for key, offset in cls.OFFSET.items():
                        my = y + offset[0]
                        mx = x + offset[1]
                        if my >= h:
                            my = h - my
                        if mx >= w:
                            mx = w - mx
                        tile |= key * map[my][mx]

                print(x, y, cls.tile_to_string(tile))
                if tile in cls.TILES:
                    tmap[y][x] = cls.TILES[tile]

        return tmap

    @classmethod
    def get_tile_map2(cls, map: np.ndarray) -> np.ndarray:
        h, w = map.shape
        tmap = np.ndarray(map.shape, dtype=int)
        tmap.fill(cls.TILES[0])
        for y in range(h):
            for x in range(w):

                if map[y][x]:
                    tile = cls.TOP_LEFT | cls.TOP | cls.TOP_RIGHT | cls.RIGHT | cls.BOTTOM_RIGHT \
                           | cls.BOTTOM | cls.BOTTOM_LEFT | cls.LEFT
                else:
                    tile = 0
                    for key, offset in cls.OFFSET.items():
                        my = y + offset[0]
                        mx = x + offset[1]
                        if my >= h:
                            my = h - my
                        if mx >= w:
                            mx = w - mx
                        tile |= key * map[my][mx]

                print(x, y, cls.tile_to_string(tile))
                tile_id = cls.get_best_match(tile)
                tmap[y][x] = tile_id

        return tmap

    @classmethod
    def get_best_match(cls, tile_key: int) -> int:
        best = None
        for key, tile in cls.TILES.items():
            count = cls.count_bits(key & tile_key)
            if best is None or count > best[0]:
                best = (count, tile)
        return best[1]

    @classmethod
    def count_bits(cls, n: int) -> int:
        count = 0
        while n:
            count += n & 1
            n >>= 1
        return count


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
        0: 1,
        TOP | RIGHT | BOTTOM | LEFT: 0,
        TOP: 81,
        RIGHT: 16,
        BOTTOM: 83,
        LEFT: 16,
        TOP | RIGHT: 18,
        TOP | LEFT: 19,
        BOTTOM | RIGHT: 10,
        BOTTOM | LEFT: 11,
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
        tmap = np.ndarray(map.shape, dtype=int)
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

                print(x, y, cls.tile_idx_to_string(tile_idx))
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

    def get_code(self):
        return """
        #line 239
        const ivec2 tile_size = ivec2(32, 32);
        const ivec2 tile_map_size = ivec2(4, 4);
        
        void mainImage(out vec4 fragColor, in vec2 fragCoord, in vec2 texCoord) {
            fragColor = texture(u_tex1, texCoord);
            
            /*
            vec2 map_pos_f = texCoord * 10.;
            ivec2 map_pos = ivec2(map_pos_f);
            vec2 tile_pos = (fract(map_pos_f)*31.+.5)/32.;
            ivec4 map = ivec4(texelFetch(u_tex2, map_pos, 0));
            tile_pos += vec2(map.x % 8, 7. - (map.x >> 3));
            //tile_pos += vec2(0, 1);
            vec4 col = texture(u_tex1, tile_pos / 8.);
            //col = vec3(map.x/64);
            fragColor = col;
            //fragColor.w = 1.;
            */
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
        ASSET_PATH
        / "wang2e.png"
        # / "mininicular.png"
    ))
    map = Map(8, 8)

    #map_tex = graph.add_node(Texture2DNode(data=np.random.random([256, 256])))
    map_tex = graph.add_node(Texture2DNode(texture=Texture2D()))
    map_tex.texture.create()
    map_tex.texture.set_active_texture(0)
    map_tex.texture.bind()
    #map_tex.texture.set_parameter(gl.GL_TEXTURE)
    map_tex.texture.mag_filter = Texture2D.GL_NEAREST
    #map_tex.texture.upload(np.array(MAP, dtype="float32"), 8, 8, gl.GL_LUMINANCE)
    map_tex.texture.upload(
        #map.map.astype("float32"),
        np.linspace(0, 64, map.width*map.height, dtype="float32"),
        #np.random.random(map.width*map.height).astype("float32") * 64,
        map.width, map.height, gl.GL_RED, gl.GL_FLOAT, gl.GL_R32F
    )

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

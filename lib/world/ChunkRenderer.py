import time
import pyglet
import glm
import math
from pyglet.gl import *
from lib.opengl import *
from lib.geom import *
from lib.world import *
from .ChunkRenderer_shader import frag_src


HEIGHTMAP2 = [
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 5, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

HEIGHTMAP1 = [
    [4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [3, 0, 5, 0, 0, 0, 0, 0, 0, 0],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [3, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [2, 0, 0, 1, 1, 1, 0, 1, 0, 0],
    [3, 0, 1, 2, 2, 2, 2, 4, 1, 0],
    [2, 0, 1, 2, 1, 1, 0, 1, 0, 0],
    [0, 0, 1, 2, 1, 0, 0, 0, 0, 0],
    [0, 0, 1, 2, 1, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

_ = 0
HEIGHTMAP = [
    [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, 2, _, _, _, _, _, _, 3, _, _, _, 2, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, 3, _, _, _, _, _, _, 2, _, _, _, 3, _, _, _, 1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 1, _, _, _],
    [_, _, 2, _, _, _, _, _, _, 3, _, 1, _, 2, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, 3, 2, 2, 2, _, _, _, 2, _, 1, _, 3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, 2, _, _, _, _, _, _, 3, _, 2, 3, 2, _, _, _, _, _, 3, _, _, _, _, _, 2, _, _, _, _, _, _, _],
    [_, _, 3, _, _, _, _, _, _, _, _, 1, _, 3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, 2, _, _, _, _, _, _, _, _, 1, _, 2, _, _, _, _, _, _, _, _, 6, _, _, _, _, _, _, _, _, _, _],
    [_, _, 3, _, _, _, _, _, _, _, _, _, _, 3, _, _, _, 5, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, 3, _, _, 1, 2, 3, 2, 1, _, _, _, 3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 1, _, _, _, _],
    [_, _, 2, _, _, 1, _, _, _, 1, _, _, _, 2, _, 2, _, _, _, _, 4, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, 3, _, _, 1, _, _, _, 1, _, _, _, 3, _, _, _, _, _, _, _, _, _, 7, _, _, _, _, _, _, _, _, _],
    [_, _, 2, _, _, _, _, _, _, _, _, _, _, 2, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, 7, 6, 7, _, _, _, _, _, _, 7, 6, 7, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, 6, 4, 6, _, _, _, _, _, _, 6, 5, 6, _, _, _, _, _, _, _, _, 2, _, _, _, _, _, _, _, _, _, _],
    [_, _, 7, 6, 7, 2, 3, _, _, 3, 2, 7, 6, 7, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, _, _, _, _, 1, _, _, 1, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, _, _, _, _, 1, _, _, 1, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, _, _, 4, 4, _, _, _, _, 4, 4, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, _, _, 4, 4, _, _, _, _, 4, 4, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
]


def gen_heightmap(w=16, h=32):
    import random
    rows = []
    for y in range(h):
        row = []
        for x in range(w):
            h = 0
            h += (math.sin(x/5.)+math.cos(y/7))*2.6
            if random.randrange(4) == 0:
                h = random.randrange(5)
            row.append(max(0, int(h)))
        rows.append(row)
    return rows



class ChunkRenderer:

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.edit_mode = False
        self.debug_view = 0

        self.load_chunk()
        self.create_opengl_objects()

    def load_chunk(self):
        self.tileset = Tileset(16, 16)
        #self.tileset.load("./assets/tileset01.png")
        self.tileset.load("./assets/tileset02.png")
        print(self.tileset)

        # ---- world chunk ----

        self.chunk = WorldChunk(self.tileset)
        self.chunk_changed = False
        if 0:
            #self.chunk.from_heightmap(gen_heightmap())
            self.chunk.from_heightmap(HEIGHTMAP, do_flip_y=True)
        else:
            tiled = TiledImport()
            self.chunk.from_tiled("./assets/tiled/level01.json")

    def create_opengl_objects(self):
        # click in world
        self.hit_voxel = (-1,-1,-1)
        self.click_mesh = LineMesh()
        self.click_mesh_changed = False
        self.click_drawable = Drawable()

        # voxel texture
        self.chunktex = None

        # distance map
        self.vdf_scale = 1
        self.vdf = self.chunk.create_voxel_distance_field(self.vdf_scale)
        self.vdf_tex = None

        # mesh and texture
        self.texture = Texture2D()
        self.mesh = self.chunk.create_mesh()
        self.drawable = self.mesh.create_drawable()
        self.drawable.shader.set_fragment_source(frag_src)

        self.texture2 = Texture2D()

        # edit mesh
        self.edit_drawable = Drawable()
        self.cur_edit_voxel = (-1,-1,-1)

        # post-fx
        if 1:
            self.fbo = Framebuffer2D(self.width, self.height)
            self.quad = ScreenQuad()
        else:
            self.fbo = None

        # player
        self.player_pos = glm.vec3(2, 2, 10) + .5
        self.splayer_pos = glm.vec3(self.player_pos)

        # projection
        self.projection = WorldProjection(self.width, self.height, WorldProjection.P_ISOMETRIC)
        self.projection.update(.4)


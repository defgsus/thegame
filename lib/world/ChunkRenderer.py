import time
import pyglet
import glm
import math
from pyglet.gl import *
from lib.opengl import *
from lib.opengl import postproc
from lib.geom import *
from lib.world import *
from .ChunkRenderer_shader import frag_src, vert_src


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

    def __init__(self, world):
        self.world = world

        self.render_settings = world.render_settings

        self.asset_id = "level01"

        self.create_opengl_objects()

    @property
    def chunk(self):
        return self.world.chunk

    def create_opengl_objects(self):

        # voxel texture
        self.chunk_tex = None

        # tileset texture
        self.tileset_tex = None

        # distance map
        self.vdf_scale = 1
        self.vdf = self.chunk.create_voxel_distance_field(self.vdf_scale)
        self.vdf_tex = None

        # level mesh
        mesh_name = "%s-mesh-drawable" % self.chunk.id
        self.mesh = self.chunk.create_mesh()
        if OpenGlAssets.has(mesh_name):
            self.mesh_drawable = OpenGlAssets.get(mesh_name)
        else:
            self.mesh_drawable = self.mesh.create_drawable()
            self.mesh_drawable.shader.set_vertex_source(vert_src)
            self.mesh_drawable.shader.set_fragment_source(frag_src)
            OpenGlAssets.register(mesh_name, self.mesh_drawable)

        # post-fx
        self.pp_blur1 = None
        self.postproc = postproc.PostProcessing()
        #self.postproc.add_stage(postproc.Wave())
        #self.postproc.add_stage(postproc.Desaturize())
        self.pp_blur1 = postproc.Blur(use_mask=True)
        self.postproc.add_stage(self.pp_blur1)
        #self.postproc.add_stage(postproc.Pixelize())

    def render(self):
        rs = self.render_settings

        glDisable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glDepthMask(True)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
        if self.chunk_tex is None:
            self.chunk_tex = self.chunk.create_texture3d()
        
        if self.vdf_tex is None:
            self.vdf_tex = self.vdf.create_texture3d("vdf")
    
        if self.tileset_tex is None:
            self.tileset_tex = self.world.tileset.create_texture2d()

        self.postproc.bind(rs)
        
        proj = rs.projection.matrix
    
        lightpos = glm.vec3(self.world.click_voxel) + (.5,.5,1.5)
        self.mesh_drawable.shader.set_uniform("u_projection", proj)
        self.mesh_drawable.shader.set_uniform("u_time", time)
        self.mesh_drawable.shader.set_uniform("u_lightpos", glm.vec4(lightpos, 1))
        self.mesh_drawable.shader.set_uniform("u_tex1", 0)
        self.mesh_drawable.shader.set_uniform("u_chunktex", 1)
        self.mesh_drawable.shader.set_uniform("u_chunksize", self.chunk.size())
        self.mesh_drawable.shader.set_uniform("u_vdf_tex", 2)
        self.mesh_drawable.shader.set_uniform("u_vdf_size", self.vdf.size())
        self.mesh_drawable.shader.set_uniform("u_vdf_scale", self.vdf_scale)
        self.mesh_drawable.shader.set_uniform("u_player_pos", self.world.agents["player"].sposition)
        self.mesh_drawable.shader.set_uniform("u_hit_voxel", self.world.click_voxel)
        self.mesh_drawable.shader.set_uniform("u_debug_view", self.world.debug_view)
    
        self.tileset_tex.set_active_texture(0)
        self.tileset_tex.bind()
        self.tileset_tex.set_active_texture(1)
        self.chunk_tex.bind()
        self.tileset_tex.set_active_texture(2)
        self.vdf_tex.bind()
        self.tileset_tex.set_active_texture(0)
    
        # main scene
        self.mesh_drawable.draw()

        # waypoints debugger
        if self.world.edit_mode:
            self.world.agents.path_debug_renderer.render(rs.projection)
    
        self.world.agents.render(rs.projection)

        # post-proc
    
        #if not self.world.edit_mode:
        ms = rs.projection.get_depth_mask_values()
        if self.pp_blur1:
            self.pp_blur1.mask_center, self.pp_blur1.mask_spread = ms
        self.postproc.render(rs)

        self.postproc.render_output(rs)

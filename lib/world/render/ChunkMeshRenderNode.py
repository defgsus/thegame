import glm

from ...opengl import *
from ...opengl.core.base import *
from .ChunkRenderer_shader import frag_src, vert_src


class ChunkMeshRenderNode(RenderNode):

    def __init__(self, world, renderer, name):
        super().__init__(name)
        self.world = world
        self.renderer = renderer
        self.mesh = None
        self.mesh_drawable = None
        self.chunk_tex = None
        self.tileset_tex = None
        self.vdf_tex = None
        self.vdf_scale = 1

    def has_depth_output(self):
        return True

    def num_multi_sample(self):
        return 16

    @property
    def chunk(self):
        return self.world.chunk

    def create(self, render_settings):
        # voxel texture
        self.chunk_tex = None

        # tileset texture
        self.tileset_tex = None

        # distance map
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

    def render(self, rs, pass_num):
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

        proj = rs.projection.matrix

        lightpos = glm.vec3(self.world.click_voxel) + (.5,.5,1.5)
        self.mesh_drawable.shader.set_uniform("u_projection", proj)
        self.mesh_drawable.shader.set_uniform("u_time", rs.time)
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

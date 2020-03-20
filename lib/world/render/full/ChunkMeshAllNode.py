import glm

from lib.opengl import *
from lib.opengl.core.base import *
from .ChunkMeshAllNode_shader import vert_src, frag_src


class ChunkMeshAllNode(RenderNode):

    def __init__(self, world, renderer, name):
        super().__init__(name)
        self.world = world
        self.renderer = renderer
        self.mesh = None
        self.mesh_drawable = None
        self.tileset_tex = None
        self.chunk_tex = None
        self.vdf_tex = None
        self.vdf_scale = 1

    def has_depth_output(self):
        return True

    def num_multi_sample(self):
        return 16

    @property
    def chunk(self):
        return self.world.chunk

    def get_code(self):
        return frag_src

    def create(self, render_settings):
        # level mesh
        mesh_name = "mesh-%s-drawable" % self.chunk.id
        print("creating mesh")
        self.mesh = self.chunk.create_mesh()
        print("done..")
        if OpenGlAssets.has(mesh_name):
            self.mesh_drawable = OpenGlAssets.get(mesh_name)
        else:
            print("creating mesh VAO")
            self.mesh_drawable = self.mesh.create_drawable("level-mesh")
            self.mesh_drawable.shader.set_vertex_source(vert_src)
            self.mesh_drawable.shader.set_fragment_source(frag_src)
            OpenGlAssets.register(mesh_name, self.mesh_drawable)
            print("done..", self.mesh_drawable)

        if self.tileset_tex is None:
            self.tileset_tex = self.world.tileset.create_texture2d()

        if self.chunk_tex is None:
            self.chunk_tex = self.world.chunk.create_texture3d()

        # voxel distance field
        if self.vdf_tex is None:
            self.vdf_tex = self.chunk.create_voxel_distance_texture3d(scale=self.vdf_scale)

    def render(self, rs, pass_num):
        if 0:
            glDisable(GL_CULL_FACE)
        else:
            glEnable(GL_CULL_FACE)
            glCullFace(GL_BACK)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glDepthMask(True)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        proj = rs.projection.matrix

        lightpos = glm.vec3(self.world.click_voxel) + glm.vec3(.5, .5, 1.5)
        shader = self.mesh_drawable.shader
        shader.set_uniform("u_projection", proj)
        shader.set_uniform("u_time", rs.time)
        shader.set_uniform("u_lightpos", glm.vec4(lightpos, 1))
        shader.set_uniform("u_color_tex", 0)
        shader.set_uniform("u_chunk_tex", 1)
        shader.set_uniform("u_vdf_tex", 2)
        shader.set_uniform("u_chunksize", self.chunk.size())
        shader.set_uniform("u_vdf_size", self.vdf_tex.size())
        shader.set_uniform("u_vdf_scale", self.vdf_scale)
        shader.set_uniform("u_player_pos", self.world.agents["player"].sposition)
        shader.set_uniform("u_hit_voxel", self.world.click_voxel)
        shader.set_uniform("u_debug_view", self.world.debug_view)

        Texture2D.set_active_texture(0)
        self.tileset_tex.bind()
        Texture2D.set_active_texture(1)
        self.chunk_tex.bind()
        Texture2D.set_active_texture(2)
        self.vdf_tex.bind()
        Texture2D.set_active_texture(0)

        # main scene
        self.mesh_drawable.draw()

        # waypoints debugger
        if self.world.edit_mode:
            self.world.agents.path_debug_renderer.render(rs.projection)

        self.world.agents.render(rs.projection)

        glDisable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)

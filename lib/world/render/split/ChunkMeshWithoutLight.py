import glm

from lib.opengl import *
from lib.opengl.core.base import *

vert_src = """
#version 130
#line 8
uniform mat4 u_projection;

in vec4 a_position;
in vec3 a_normal;
in vec4 a_color;
in vec2 a_texcoord;
in vec3 a_ambient;

out vec4 v_pos;
out vec3 v_normal;
out vec4 v_color;
out vec2 v_texcoord;
out vec3 v_ambient;

void main()
{
    v_pos = a_position;
    v_normal = a_normal;
    v_color = a_color;
    v_texcoord = a_texcoord;
    v_ambient = a_ambient;
    gl_Position = u_projection * a_position;
}

"""

frag_src = """
#version 130
#line 37
uniform sampler2D u_tex1;
uniform sampler3D u_vdf_tex;

uniform float u_time;
uniform vec3 u_chunksize;
uniform vec3 u_vdf_size;
uniform float u_vdf_scale;

in vec4 v_pos;
in vec3 v_normal;
in vec2 v_texcoord;
in vec3 v_ambient;

out vec4 fragColor;

float distance_at(in vec3 pos) {
    pos /= u_vdf_scale;
    if (any(lessThan(pos, vec3(0))) || any(greaterThanEqual(pos, u_chunksize)))
        return 15.;
    return texture(u_vdf_tex, pos / u_chunksize).x / u_vdf_scale;
}

void main() {
    vec4 tex = texture2D(u_tex1, v_texcoord);
    
    // ambient occlusion    
    vec3 col = tex.xyz * pow(distance_at(v_pos.xyz), .5);
    col *= v_ambient;
    
    fragColor = vec4(col, 1);
}
"""


class ChunkMeshWithoutLight(RenderNode):

    def __init__(self, world, renderer, name):
        super().__init__(name)
        self.world = world
        self.renderer = renderer
        self.mesh = None
        self.mesh_drawable = None
        self.tileset_tex = None
        self.vdf_tex = None
        self.vdf_scale = 1

    def num_color_outputs(self):
        return 1

    def has_depth_output(self):
        return True

    def num_multi_sample(self):
        return 16

    @property
    def chunk(self):
        return self.world.chunk

    def create(self, render_settings):
        # level mesh
        mesh_name = "%s-mesh-nol-drawable" % self.chunk.id
        self.mesh = self.chunk.create_mesh()
        if OpenGlAssets.has(mesh_name):
            self.mesh_drawable = OpenGlAssets.get(mesh_name)
        else:
            self.mesh_drawable = self.mesh.create_drawable()
            self.mesh_drawable.shader.set_vertex_source(vert_src)
            self.mesh_drawable.shader.set_fragment_source(frag_src)
            OpenGlAssets.register(mesh_name, self.mesh_drawable)

        if self.tileset_tex is None:
            self.tileset_tex = self.world.tileset.create_texture2d()

        # voxel distance field
        if self.vdf_tex is None:
            self.vdf_tex = self.chunk.create_voxel_distance_texture3d(scale=self.vdf_scale)

    def render(self, rs, pass_num):
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glEnable(GL_DEPTH_TEST)
        glDepthMask(True)
        glDisable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        proj = rs.projection.matrix

        self.mesh_drawable.shader.set_uniform("u_projection", proj)
        self.mesh_drawable.shader.set_uniform("u_tex1", 0)
        self.mesh_drawable.shader.set_uniform("u_vdf_tex", 1)
        self.mesh_drawable.shader.set_uniform("u_chunksize", self.chunk.size())
        self.mesh_drawable.shader.set_uniform("u_vdf_size", self.vdf_tex.size())
        self.mesh_drawable.shader.set_uniform("u_vdf_scale", self.vdf_scale)

        Texture2D.set_active_texture(0)
        self.tileset_tex.bind()
        Texture2D.set_active_texture(1)
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

import glm

from lib.opengl import *
from lib.opengl.core.base import *

vert_src = DEFAULT_SHADER_VERSION + """
#line 7
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
out mat3 v_normal_space;

/** Returns the matrix to multiply the light-direction normal */
mat3 calc_light_matrix(mat4 transform)
{
    // normal in world coordinates
    vec3 norm = transpose(inverse(mat3(transform))) * a_normal;

    vec3 tangent =  vec3(-norm.z, -norm.y,  norm.x);
    vec3 binormal = vec3(-norm.x,  norm.z, -norm.y);
    return mat3(tangent, -binormal, norm);
}

void main()
{
    v_pos = a_position;
    v_normal = a_normal;
    v_color = a_color;
    v_texcoord = a_texcoord;
    v_ambient = a_ambient;
    v_normal_space = calc_light_matrix(mat4(1));
    gl_Position = u_projection * a_position;
}

"""

frag_src = DEFAULT_SHADER_VERSION + """
#line 48
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
in mat3 v_normal_space;

out vec4 fragColor;
out vec4 fragNormal;
out vec4 fragPosition;

float distance_at(in vec3 pos) {
    pos /= u_vdf_scale;
    if (any(lessThan(pos, vec3(0))) || any(greaterThanEqual(pos, u_chunksize)))
        return 15.;
    return texture(u_vdf_tex, pos / u_chunksize).x / u_vdf_scale;
}

void main() {
    vec4 tex = texture2D(u_tex1, v_texcoord);
    
    // bump-mapping        
    vec3 normal = vec3(0, 0, 1);        
    vec2 v_normcoord = v_texcoord + vec2(.5, 0.);
    vec4 normal_texel = texture2D(u_tex1, v_normcoord);
    normal = normalize(mix(normal, normal_texel.xyz, normal_texel.w));
    normal = v_normal_space * normal;
    
    vec3 col = tex.xyz * pow(distance_at(v_pos.xyz), .5);
    
    fragColor = vec4(col, 1);
    fragColor.xyz *= v_ambient;
    fragNormal = vec4(normal, 1);
    fragPosition = vec4(v_pos.xyz, 1);
}
"""


class ChunkMeshRenderNode(RenderNode):

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
        return 3

    def has_depth_output(self):
        return True

    def num_multi_sample(self):
        return 16

    @property
    def chunk(self):
        return self.world.chunk

    def create(self, render_settings):
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

        if self.tileset_tex is None:
            self.tileset_tex = self.world.tileset.create_texture2d()

        # voxel distance field
        if self.vdf_tex is None:
            self.vdf_tex = self.chunk.create_voxel_distance_texture3d(scale=self.vdf_scale)

    def render(self, rs, pass_num):
        glDisable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glDepthMask(True)
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

import glm

from ...opengl import *
from ...opengl.core.base import *
from ...geom import MeshFactory, LineMesh

vert_src = DEFAULT_SHADER_VERSION + """
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
#line 50
uniform sampler2D u_tex1;
uniform float u_time;

in vec4 v_pos;
in vec3 v_normal;
in vec2 v_texcoord;
in vec3 v_ambient;
in mat3 v_normal_space;

out vec4 fragColor;

void main() {
    vec4 tex = texture2D(u_tex1, v_texcoord);
    
    // bump-mapping        
    vec3 normal = vec3(0, 0, 1);        
    vec2 v_normcoord = v_texcoord + vec2(.5, 0.);
    vec4 normal_texel = texture2D(u_tex1, v_normcoord);
    normal = normalize(mix(normal, normal_texel.xyz, normal_texel.w));
    normal = v_normal_space * normal;
    
    vec3 col = tex.xyz;
    
    // simple lighting
    vec3 ln = normalize(vec3(100) - v_pos.xyz);
    float ld = max(0., dot(normal, ln));
    col = col * .7 + .3 * ld;
    
    col *= v_ambient;
    
    fragColor = vec4(col, 1);
}
"""


class ChunkMeshNode(RenderNode):

    def __init__(self, edit_id, chunk, name):
        super().__init__(name)
        self.edit_id = edit_id
        self.chunk = chunk
        self.mesh = None
        self.mesh_drawable = None
        self._mesh_changed = True
        self.edit_mesh = LineMesh()
        self.edit_mesh_drawable = None
        self.tileset_tex = None
        self._focus_voxel = None
        self._edit_mesh_changed = False

    def has_depth_output(self):
        return True

    def num_multi_sample(self):
        return 9

    @property
    def focus_voxel(self):
        return self._focus_voxel

    @focus_voxel.setter
    def focus_voxel(self, voxel):
        self._focus_voxel = voxel
        self._edit_mesh_changed = True

    def create(self, render_settings):
        self.updateGl()

    def render(self, rs, pass_num):
        self.updateGl()

        glDisable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glDepthMask(True)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        proj = rs.projection.matrix

        if self.mesh_drawable is not None:
            self.mesh_drawable.shader.set_uniform("u_projection", proj)
            self.mesh_drawable.shader.set_uniform("u_tex1", 0)

            Texture2D.set_active_texture(0)
            self.tileset_tex.bind()

            # main scene
            self.mesh_drawable.draw()

        if self.edit_mesh_drawable is not None:
            self.edit_mesh_drawable.shader.set_uniform("u_projection", proj)
            self.edit_mesh_drawable.draw()

        glDisable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)

    def updateGl(self):
        if self.tileset_tex is None:
            self.tileset_tex = self.chunk.tileset.create_texture2d(self.edit_id)

        if self._mesh_changed:
            self._mesh_changed = False
            self.mesh = self.chunk.create_mesh(do_ambient=False)
            if self.mesh.is_empty():
                if self.mesh_drawable:
                    self.mesh_drawable.release()
                    self.mesh_drawable = None
            else:
                if self.mesh_drawable is None:
                    self.mesh_drawable = Drawable("%s-meshdraw" % self.edit_id)
                    self.mesh_drawable.shader.set_vertex_source(vert_src)
                    self.mesh_drawable.shader.set_fragment_source(frag_src)
                self.mesh.update_drawable(self.mesh_drawable)

        if self._edit_mesh_changed:
            self._edit_mesh_changed = False
            self.edit_mesh.clear()
            if self._focus_voxel is not None:
                self.edit_mesh.set_color(.5, 1, 1)
                MeshFactory.add_cube(self.edit_mesh, origin=glm.vec3(self.focus_voxel)+.5, size=glm.vec3(1.1))

            if self.edit_mesh.is_empty():
                if self.edit_mesh_drawable:
                    self.edit_mesh_drawable.release()
                    self.edit_mesh_drawable = None
            else:
                if self.edit_mesh_drawable is None:
                    self.edit_mesh_drawable = Drawable("%s-editmeshdraw" % self.edit_id)
                self.edit_mesh.update_drawable(self.edit_mesh_drawable)



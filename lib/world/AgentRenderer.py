import glm

from .Tileset import Tileset
from ..geom import TriangleMesh
from ..opengl import Drawable
from ..pector import quat


VERTEX_SRC = """
#version 130
uniform mat4 u_projection;

in vec4 a_position;
in vec2 a_texcoord;

out vec4 v_pos;
out vec2 v_texcoord;

void main()
{
    v_pos = a_position;
    v_texcoord = a_texcoord;
    gl_Position = u_projection * a_position;
}
"""

FRAGMENT_SRC = """
#version 130
uniform sampler2D u_tex1;
uniform vec2 u_tex_offset;

in vec4 v_pos;
in vec2 v_texcoord;

out vec4 fragColor;

void main() {
    vec4 col = texture(u_tex1, v_texcoord + u_tex_offset);
    if (col.w < 0.01)
        discard;
    fragColor = col;
}
"""


class AgentRenderer:

    DOWN = 1
    LEFT = 2
    UP = 3
    RIGHT = 4

    def __init__(self, filename="./assets/pokeson.png"):
        self.tileset = Tileset(32, 32)
        self.tileset.load(filename)
        #print("agent", self.tileset)
        self.texture = None
        self.mesh = TriangleMesh()
        self.drawable = Drawable()
        self.drawable.shader.set_vertex_source(VERTEX_SRC)
        self.drawable.shader.set_fragment_source(FRAGMENT_SRC)

        s = 1
        uv = self.tileset.get_uv_quad(0)
        self.mesh.add_quad((-s, 0, 0), (s, 0, 0), (s, 2*s, 0), (-s, 2*s, 0), *uv)

    def release(self):
        if self.texture is not None and self.texture.is_created():
            self.texture.release()
        self.drawable.release()

    def render(self, projection, pos, dir, frame_num):
        self._update()

        trans = projection.matrix

        mat = glm.translate(trans, pos + (0,0,0))

        p1 = mat * glm.vec4(0,0,0,1)
        p2 = mat * glm.vec4(0,1,0,1)
        p = p2 - p1
        a = glm.atan(p.x, p.y)
        mat = glm.rotate(mat, a, (0,0,1))

        mat = glm.rotate(mat, glm.pi()/2., (1,0,0))

        tile_idx = self.get_tileset_idx(dir, frame_num)

        self.texture.bind()
        self.drawable.shader.set_uniform("u_projection", mat)
        self.drawable.shader.set_uniform("u_tex_offset", self.tileset.get_uv_offset(tile_idx))
        self.drawable.draw()

    def _update(self):
        if not self.texture:
            self.texture = self.tileset.create_texture2d()

        if self.drawable.is_empty():
            self.mesh.update_drawable(self.drawable)

    def get_tileset_idx(self, dir, frame_num):
        idx = (dir-1) * self.tileset.width + frame_num
        return idx


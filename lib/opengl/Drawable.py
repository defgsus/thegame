from .base import *
from .Shader import Shader
from .VertexArrayObject import VertexArrayObject



DEFAULT_VERTEX_SRC = """
#version 130
uniform mat4 u_projection;

in vec4 a_position;
in vec3 a_normal;
in vec2 a_texcoord;

out vec4 v_pos;
out vec3 v_normal;
out vec2 v_texcoord;

void main()
{
    v_pos = a_position;
    v_normal = a_normal;
    v_texcoord = a_texcoord;
    gl_Position = u_projection * a_position;
}
"""

DEFAULT_FRAGMENT_SRC = """
#version 130
uniform sampler2D u_tex1;

in vec4 v_pos;
in vec3 v_normal;
in vec2 v_texcoord;

out vec4 fragColor;

void main() {
    vec4 col = texture(u_tex1, v_texcoord);
    col.xyz += v_normal*.3;
    fragColor = col;
}
"""


class Drawable:

    A_POSITION = "a_position"
    A_NORMAL = "a_normal"
    A_TEXCOORD = "a_texcoord"
    A_COLOR = "a_color"

    def __init__(self):
        self.vao = VertexArrayObject()
        self.shader = Shader(DEFAULT_VERTEX_SRC, DEFAULT_FRAGMENT_SRC)
        self._attributes_changed = True
        self._attributes = dict()
        self._elements = dict()

    def release(self):
        if self.vao.is_created():
            self.vao.release()
        if self.shader.is_created():
            self.shader.release()

    def set_attribute(self, name, num_coords, values, Type=GLfloat):
        self._attributes[name] = (num_coords, values, Type)
        self._attributes_changed = True

    def set_index(self, primitive_type, values, Type=GLuint):
        self._elements[primitive_type] = (values, Type)
        self._attributes_changed = True

    def draw(self):
        if not self.shader.is_created():
            self.shader.create()
        if not self.shader.is_compiled() or self.shader.is_source_changed():
            self.shader.compile()

        if self._attributes_changed:
            if self.vao.is_created():
                self.vao.release()
            self._attributes_changed = False

        if not self.vao.is_created():
            self.vao.create()
            self.vao.bind()
            for a_name in self._attributes:
                att = self._attributes[a_name]
                if self.shader.has_attribute(a_name):
                    self.vao.create_attribute_buffer(
                        self.shader.attribute(a_name).location,
                        att[0], att[2], att[1]
                    )
            for prim_type in self._elements:
                elem = self._elements[prim_type]
                self.vao.create_element_buffer(prim_type, elem[1], elem[0])

        self.shader.bind()
        self.shader.update_uniforms()
        self.vao.draw_elements()




from .base import *
from .Shader import Shader
from .VertexArrayObject import VertexArrayObject



DEFAULT_VERTEX_SRC = """
#version 130
in vec4 a_position;
out vec4 v_pos;
void main()
{
    v_pos = a_position;
    gl_Position = a_position;
}
"""

DEFAULT_FRAGMENT_SRC = """
#version 130
in vec4 v_pos;
out vec4 fragColor;
uniform vec2 u_resolution;
uniform vec2 u_mouse_uv;
void main() {
    fragColor = vec4(1,1,0,1);
}
"""



class Drawable:

    A_POSITION = "a_position"
    A_NORMAL = "a_normal"
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
                self.vao.create_attribute_buffer(
                    self.shader.attribute(a_name).location,
                    att[0], att[2], att[1]
                )
            for prim_type in self._elements:
                elem = self._elements[prim_type]
                self.vao.create_element_buffer(prim_type, elem[1], elem[0])

        self.shader.bind()
        self.vao.draw_elements()




import glm

from . import DEFAULT_SHADER_VERSION
from .core.base import *
from .core.Shader import Shader
from .core.VertexArrayObject import VertexArrayObject



DEFAULT_VERTEX_SRC = DEFAULT_SHADER_VERSION + """
#line 11
uniform mat4 u_projection;
uniform mat4 u_transformation;
uniform mat4 u_transformation_inv;

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
out vec3 v_world_normal;

void main()
{
    v_pos = a_position;
    v_normal = a_normal;
    v_world_normal = normalize((vec4(a_normal, 0.) * u_transformation_inv).xyz);
    v_color = a_color;
    v_texcoord = a_texcoord;
    v_ambient = a_ambient;
    gl_Position = u_projection * u_transformation * a_position;
}
"""

DEFAULT_FRAGMENT_SRC = DEFAULT_SHADER_VERSION + """
#line 36
uniform sampler2D u_tex1;

in vec4 v_pos;
in vec4 v_color;
in vec3 v_normal;
in vec2 v_texcoord;

out vec4 fragColor;

void main() {
    vec4 col = v_color;
    //col += texture(u_tex1, v_texcoord);
    //col.xyz += v_normal*.3;
    fragColor = col;
}
"""


class Drawable:
    """
    Binds a VertexArrayObject and a Shader together
    """

    A_POSITION = "a_position"
    A_NORMAL = "a_normal"
    A_TEXCOORD = "a_texcoord"
    A_COLOR = "a_color"

    def __init__(self, name: str = None):
        self.name = name or "drawable"
        self.vao = VertexArrayObject()
        self.shader = Shader(DEFAULT_VERTEX_SRC, DEFAULT_FRAGMENT_SRC, name="%s-shader" % (self.name))
        self.shader.set_uniform("u_projection", glm.mat4(1))
        self.shader.set_uniform("u_transformation", glm.mat4(1))
        self.shader.set_uniform("u_transformation_inv", glm.mat4(1))
        self._attributes_changed = True
        self._attributes = dict()
        self._elements = dict()

    def __str__(self):
        return "%s(%s, %s, %s)" % (
            self.__class__.__name__,
            self.name,
            ", ".join("'%s'" % e for e in sorted(self._attributes)),
            ", ".join("%s" % e for e in sorted(self._elements)),
        )

    def is_empty(self):
        return not self._elements

    def release(self):
        if self.vao.is_created():
            self.vao.release()
        if self.shader.is_created():
            self.shader.release()

    def clear_attributes(self):
        self._attributes.clear()
        self._attributes_changed = True

    def clear_index(self):
        self._elements.clear()
        self._attributes_changed = True

    def clear(self):
        self.clear_attributes()
        self.clear_index()

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
                        attribute_location=self.shader.attribute(a_name).location,
                        num_dimensions=att[0], Type=att[2], values=att[1]
                    )
            for prim_type in self._elements:
                elem = self._elements[prim_type]
                self.vao.create_element_buffer(prim_type, elem[1], elem[0])

        self.shader.bind()
        self.shader.update_uniforms()
        self.vao.draw_elements()

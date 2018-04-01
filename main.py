import pyglet
from lib.opengl.VertexArrayObject import *
from lib.opengl.Shader import *

vert_src = """
#version 130
in vec4 a_position;
out vec4 v_pos;
void main()
{
    v_pos = a_position;
    gl_Position = a_position;
}
"""

frag_src = """
#version 130
in vec4 v_pos;
out vec4 fragColor;
uniform vec2 u_resolution;
uniform vec2 u_mouse_uv;
uniform vec4 u_color;
uniform vec4 u_color2;
void main() {
    fragColor = vec4(1,1,0,1) + u_color + u_color2;
}
"""


class MainWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.vao = VertexArrayObject()
        self.buf = ArrayBufferObject()
        self.shader = Shader(vert_src, frag_src)

    def on_draw(self):
        self.clear()
        if not self.shader.is_created():
            self.shader.create()
            self.shader.compile()
            self.shader.dump_variables()
        if not self.vao.is_created():
            self.vao.create()
            self.vao.create_attribute_buffer(self.shader.attribute("a_position").location, 3,
                                             GLfloat, [0,0,0, 100,0,0, 100,100,0, 0,100,0])
            self.vao.create_element_buffer(GL_TRIANGLES, GLuint, [0,1,2, 0,2,3])

        self.shader.bind()
        self.vao.bind()
        self.vao.draw_elements()

        OpenGlBaseObject.dump_instances()





platform = pyglet.window.get_platform()
display = platform.get_default_display()
gl_config = pyglet.gl.Config(
    major_version=3,
    minor_version=0,
    double_buffer=True,
)
main_window = MainWindow(config=gl_config, resizable=True)

pyglet.app.run()

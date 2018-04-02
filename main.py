import pyglet
from lib.opengl.VertexArrayObject import *
from lib.opengl.Shader import *
from lib.opengl.Drawable import Drawable

frag_src = """
#version 130
in vec4 v_pos;
out vec4 fragColor;
uniform vec2 u_resolution;
uniform vec2 u_mouse_uv;
uniform vec4 u_color;
uniform vec4 u_color2;
void main() {
    fragColor = vec4(abs(v_pos.xy), 0, 1);
}
"""


class MainWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.mesh = Drawable()
        self.mesh.set_attribute(
            self.mesh.A_POSITION,
            2, [-1,-1, 1,-1, 1,1, -1,1])
        self.mesh.set_index(GL_TRIANGLES, [0,1,2, 0,2,3])
        self.mesh.shader.set_fragment_source(frag_src)

    def on_draw(self):
        self.mesh.draw()
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

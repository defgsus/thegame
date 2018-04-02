import pyglet
import glm
from lib.opengl.VertexArrayObject import *
from lib.opengl.Shader import *
from lib.opengl.Drawable import Drawable
from lib.geom.TriangleMesh import TriangleMesh

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


class TestDrawableWindow(pyglet.window.Window):

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


class MainWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.mesh = TriangleMesh()
        #self.mesh.add_triangle([-1,-1,0], [1,-1,0], [1,1,0])
        #self.mesh.add_triangle([-1,-1,0], [1,1,0], [-1,1,0.5])
        import random
        def heightmap(x, y):
            return random.randrange(2)/10
        self.mesh.create_height_map(10,10, heightmap, 1./10)
        self.drawable = self.mesh.get_drawable()
        self.rotate_x = glm.pi()/3.

    def on_draw(self):
        self.clear()
        proj = glm.ortho(0,1, -1,1, -2, 2)
        proj = glm.rotate(proj, self.rotate_x, (1,0,0))
        print(proj)
        self.drawable.shader.set_uniform("u_projection", proj)
        self.drawable.draw()
        OpenGlBaseObject.dump_instances()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.rotate_x += scroll_y / 30.



platform = pyglet.window.get_platform()
display = platform.get_default_display()
gl_config = pyglet.gl.Config(
    major_version=3,
    minor_version=0,
    double_buffer=True,
)
main_window = MainWindow(config=gl_config, resizable=True)

pyglet.app.run()

from lib.opengl.core.Shader import *
from lib.opengl.Drawable import Drawable


class TestWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(TestWindow, self).__init__(*args, **kwargs)
        self.mesh = Drawable()
        self.mesh.set_attribute(
            self.mesh.A_POSITION,
            2, [-1,-1, 1,-1, 1,1, -1,1])
        self.mesh.set_index(GL_TRIANGLES, [0,1,2, 0,2,3])

    def on_draw(self):
        self.mesh.draw()
        OpenGlObjects.dump()


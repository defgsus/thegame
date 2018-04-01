import pyglet
from lib.opengl.VertexArrayObject import *


class MainWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.vao = VertexArrayObject()
        self.buf = ArrayBufferObject()

    def on_draw(self):
        self.clear()
        if not self.vao.is_created():
            self.vao.create()
            self.vao.create_attribute_buffer(0, 3, GLfloat, [1,2,3, 4,5,6, 7,8,9, 10,11,12])
            self.vao.create_element_buffer(GL_TRIANGLES, GLuint, [0,1,2, 0,2,3])
        #if not self.buf.is_created():
        #    self.buf.create()
        #    self.buf.bind()
        #    self.buf.upload(GLfloat, [0,1,2,3])

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

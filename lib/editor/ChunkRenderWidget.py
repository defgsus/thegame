from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *

from lib.opengl import *
from lib.world.render import RenderSettings
from lib.world import WorldEngine


class ColorNode(RenderNode):

    def __init__(self, name):
        super().__init__(name)
        self.quad = ScreenQuad()
        self.quad.set_shader_code("""
        #line 20
        void mainImage(out vec4 fragColor, in vec2 fragCoord, in vec2 texCoord) {
            //fragColor = texture(u_tex1, texCoord);
            vec3 col = .5 + .5 * sin(texCoord.xyx * vec3(1,1,1.3) * 2 + u_time * vec3(3,5,7)/5.);
            fragColor = vec4(col, 1);
        }
        """)

    def release(self):
        self.quad.release()

    def render(self, rs, pass_num):
        self.quad.drawable.shader.set_uniform("u_time", rs.time)
        self.quad.draw(rs.render_width, rs.render_height)


class GridNode(RenderNode):

    def __init__(self, name):
        super().__init__(name)
        self.quad = ScreenQuad()
        self.quad.set_shader_code("""
        #line 42
        void mainImage(out vec4 fragColor, in vec2 fragCoord, in vec2 texCoord) {
            vec2 mp = mod(texCoord * 10., 1.);
            float grid = max(smoothstep(.1,.0,abs(mp.x-.5)), smoothstep(.1,.0,abs(mp.y-.5)));
            fragColor = vec4(vec3(grid), 1);
        }
        """)

    def release(self):
        self.quad.release()

    def render(self, rs, pass_num):
        self.quad.drawable.shader.set_uniform("u_time", rs.time)
        self.quad.draw(rs.render_width, rs.render_height)



class ChunkRenderWidget(QGLWidget):

    def __init__(self, parent):
        super().__init__(parent)

        #self.render_settings = RenderSettings(self.width(), self.height())
        #self.graph = RenderGraph()
        #self.graph.add_node(ColorNode("color"))
        #self.pipeline = self.graph.create_pipeline()
        self.engine = WorldEngine()
        self.render_settings = self.engine.render_settings

    def initializeGL(self):
        pass

    def resizeGL(self, w, h):
        print(w, h)
        #self.render_settings.render_width = w
        #self.render_settings.render_height = h

    def paintGL(self):
        self.render_settings.screen_width = self.width()
        self.render_settings.screen_height = self.height()

        #self.pipeline.render(self.render_settings)
        #self.pipeline.render_to_screen(self.render_settings)
        self.engine.render(0)

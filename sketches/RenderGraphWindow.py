import pyglet

from lib.opengl import *
from lib.world import *


class SomeNode(RenderNode):

    def __init__(self, name):
        super().__init__(name)
        self.quad = ScreenQuad()
        self.quad.set_shader_code("""
        #line 13
        void mainImage(out vec4 fragColor, in vec2 fragCoord, in vec2 texCoord) {
            //fragColor = texture(u_tex1, texCoord);
            fragColor = vec4(texCoord, 0, 1);
        }
        """)

    def release(self):
        self.quad.release()

    def render(self, rs):
        self.quad.draw(rs.render_width, rs.render_height)


class RenderGraphWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(RenderGraphWindow, self).__init__(*args, **kwargs)

        self.render_settings = RenderSettings(320, 200)

        self.graph = RenderGraph()
        self.graph.add_node(SomeNode("node01"))
        self.graph.add_node(SomeNode("node02"))
        self.graph.connect("node01", 0, "node02", 0)
        self.pipeline = self.graph.create_pipeline()
        print(self.pipeline.stages)
        self.pipeline.dump()

    def on_draw(self):
        self.clear()
        self.render_settings.screen_width = self.width
        self.render_settings.screen_height = self.height

        self.pipeline.render(self.render_settings)

        self.pipeline.render_to_screen(self.render_settings)


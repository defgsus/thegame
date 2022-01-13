import time
import traceback

import pyglet
import glm

from lib.opengl.core.base import *
from lib.opengl import *
from lib.opengl import postproc
from lib.world import *
from lib.world.render import *
from lib.geom import *


class CoordinateGridNode(RenderNode):
    def __init__(self, name):
        super().__init__(name)
        self.grid = CoordinateGrid(20)

    def num_multi_sample(self):
        return 32

    def has_depth_output(self):
        return True

    def release(self):
        self.grid.release()

    def render(self, rs, pass_num):
        self.grid.drawable.shader.set_uniform("u_projection", rs.projection.matrix)
        self.grid.drawable.draw()


class RenderGraphWindow(pyglet.window.Window):

    def __init__(self, render_graph, render_settings=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.render_settings = render_settings or RenderSettings(320, 320)
        self.live_transform = LiveTransformation()
        self.init_transform()

        self.graph = render_graph
        #self.graph = RenderGraph()
        #self.graph.add_node(CoordinateGridNode("grid"))

        self.pipeline = self.graph.create_pipeline()
        self.pipeline.dump()
        #self.pipeline.verbose = 5

        self.start_time = time.time()
        pyglet.clock.schedule_interval(self.update, 1.0 / 60.0)

    def set_render_graph(self, render_graph):
        if self.graph:
            pass # self.graph.destroy?
        self.graph = render_graph
        self.pipeline = self.graph.create_pipeline()
        self.pipeline.dump()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if dx:
            self.live_transform.rotate_y(dx * .2)
        if dy:
            self.live_transform.rotate_x(-dy * .2)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.live_transform.translate_z(scroll_y * 4.)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.close()

    def on_text(self, text):
        if text == "f":
            self.set_fullscreen(not self.fullscreen)
        if text in "po":
            self.init_transform()
            self.render_settings.projection.init(text)
        if text == "+":
            self.live_transform.translate_z(2)
        if text == "-":
            self.live_transform.translate_z(-2)

    def init_transform(self):
        self.live_transform.init()
        self.live_transform.translate_z(-13)

    def update(self, dt):
        self.live_transform.update(dt)
        self.render_settings.projection.update(min(1, dt*1))

    def on_draw(self):
        try:
            self.clear()
            self.render_settings.screen_width = self.width
            self.render_settings.screen_height = self.height
            self.render_settings.time = time.time() - self.start_time
            self.render_settings.projection.transformation_matrix = self.live_transform.matrix

            glDisable(GL_CULL_FACE)
            glEnable(GL_DEPTH_TEST)
            glDepthMask(True)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            self.pipeline.render(self.render_settings)

            self.pipeline.render_to_screen(self.render_settings)

        except Exception as e:
            traceback.print_exc()
            # print(f"{e.__class__.__name__}: {e}")
            exit(-1)

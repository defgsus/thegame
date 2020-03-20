import time

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

        self.render_settings = render_settings or RenderSettings(320, 200)

        self.graph = render_graph
        # self.graph.add_node(CoordinateGridNode("grid"))

        self.pipeline = self.graph.create_pipeline()
        self.pipeline.dump()
        #self.pipeline.verbose = 5

        self.rotate_x = 0.
        self.rotate_y = 0.

        self.start_time = time.time()
        pyglet.clock.schedule_interval(self.update, 1.0 / 60.0)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.rotate_y += dx / 30.
        self.rotate_x += dy / 30.

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.close()

    def on_text(self, text):
        if text == "f":
            self.set_fullscreen(not self.fullscreen)

    def update(self, dt):
        self.render_settings.projection.user_transformation = self._calc_trans_matrix()
        self.render_settings.projection.update(min(1, dt*2))

    def on_draw(self):
        try:
            self.clear()
            self.render_settings.screen_width = self.width
            self.render_settings.screen_height = self.height
            self.render_settings.time = time.time() - self.start_time

            glDisable(GL_CULL_FACE)
            glEnable(GL_DEPTH_TEST)
            glDepthMask(True)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            self.pipeline.render(self.render_settings)

            self.pipeline.render_to_screen(self.render_settings)

        except Exception as e:
            print(f"{e.__class__.__name__}: {e}")
            exit(-1)

    def _calc_trans_matrix(self):
        trans = glm.translate(glm.mat4(1), glm.vec3(0, 0, 4))
        trans = glm.rotate(trans, self.rotate_x, glm.vec3(1, 0, 0))
        trans = glm.rotate(trans, self.rotate_y, glm.vec3(0, 1, 0))
        return trans

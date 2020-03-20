import time
import pyglet
import glm
import math
from pyglet.gl import *
from lib.opengl import *

from lib.world import *


class ProjectionWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(ProjectionWindow, self).__init__(
            *args,
            #width=800, height=600,
            vsync=True, **kwargs)

        self.coordinate_grid = CoordinateGrid(20)

        self.drawable = Drawable()
        self.drawable.set_attribute("a_position", 3, [0,0,0, 1,0,0, 1,1,0, 0,1,0])
        self.drawable.set_attribute("a_texcoord", 2, [0,0, 1,0, 1,1, 0,1])
        self.drawable.set_index(GL_TRIANGLES, [0,1,2, 0,2,3])

        self.texture = Texture2D()

        self.fov = 1.
        self._projection = "o"
        self._init_rotation()
        self._calc_projection()

        self.start_time = time.time()

        pyglet.clock.schedule_interval(self.update, 1.0 / 60.0)
        # pyglet.clock.set_fps_limit(60)

    def update(self, dt):
        self.check_keys(dt)

    def check_keys(self, dt):
        pass

    def on_draw(self):
        glDisable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        self.clear()

        self._calc_projection()

        if not self.texture.is_created():
            self.texture.create()
            self.texture.bind()
            self.texture.upload_image("./assets/F.png")

        self.drawable.shader.set_uniform("u_projection", self.projection_matrix)
        self.drawable.draw()

        self.coordinate_grid.drawable.shader.set_uniform("u_projection", self.projection_matrix)
        self.coordinate_grid.draw()



    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.rotate_x += scroll_y / 30.

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.rotate_y += dx / 30.

    def on_mouse_press(self, x, y, button, modifiers):
        ro, rd = self.get_ray(x, y)
        print(ro, rd)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.close()

    def on_text(self, text):
        if text == "o":
            self._projection = "o"
            self._init_rotation()
        if text == "i":
            self._projection = "i"
            self._init_rotation()
            self.rotate_z = glm.pi()/4
        if text == "p":
            self._projection = "p"
            self._init_rotation()
        if text == "e":
            self._projection = "e"
            self._init_rotation()
        if text == "f":
            self.set_fullscreen(not self.fullscreen)
        if text == "+":
            self.zoom += 1.
        if text == "-":
            self.zoom -= 1.
        if text == "a":
            self.fov += 0.01
            print(self.fov)

    def get_uv(self, x, y):
        return ((x / self.width * 2. - 1.) * self.width / self.height,
                y / self.height * 2. - 1.)

    def get_ray(self, x, y):
        uv = self.get_uv(x, y)
        ro = glm.vec3(self.projection_matrix[3])
        m = glm.mat4(self.projection_matrix)
        m[3][0] = 0
        m[3][1] = 0
        m[3][2] = 0
        rd = m * glm.vec4(glm.normalize(glm.vec3(uv[0], uv[1], -1.2)), 0)
        return (ro, rd)

    def _calc_projection(self):
        asp = self.width / self.height

        if self._projection == "o":
            proj = glm.ortho(-3, 3, -3, 3, -30, 30)
        elif self._projection == "p":
            proj = glm.perspectiveFov(self.fov, self.width, self.height, 0.01, 100.)

        proj = glm.translate(proj, glm.vec3(0,0,-4))

        self.projection_matrix = proj

    def _init_rotation(self):
        pass
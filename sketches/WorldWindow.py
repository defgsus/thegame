import time
import pyglet
import glm
import math
from pyglet.gl import *
from lib.opengl import *
from lib.geom import *

from lib.world import *
from lib.world.ChunkRenderer_shader import vert_src, frag_src
from lib.ai import *


class WorldWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(WorldWindow, self).__init__(
            *args,
            #width=800, height=600,
            vsync=True, **kwargs)

        self.world = WorldEngine(self.width, self.height)

        self.edit_mode = False
        self.debug_view = 0

        self.keys = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keys)

        # time(r)
        self.start_time = time.time()
        pyglet.clock.schedule_interval(self.update, 1.0 / 60.0)
        pyglet.clock.set_fps_limit(60)

    def update(self, dt):
        self.check_keys(dt)
        self.world.screen_width = self.width
        self.world.screen_height = self.height
        self.world.update(dt)

    def check_keys(self, dt):
        dir_mapping = {
            pyglet.window.key.LEFT: glm.vec3(-1,0,0),
            pyglet.window.key.RIGHT: glm.vec3(1,0,0),
            pyglet.window.key.UP: glm.vec3(0,1,0),
            pyglet.window.key.DOWN: glm.vec3(0,-1,0),
            #pyglet.window.key.SPACE: glm.vec3(0,0,1),
        }
        sum_dir = glm.vec3(0)
        num = 0
        for symbol in dir_mapping:
            if self.keys[symbol]:
                dir = dir_mapping[symbol]
                if self.world.projection.projection == self.world.projection.P_ISOMETRIC:
                    dir = glm.vec3(glm.rotate(glm.mat4(1), -glm.pi()/4., (0,0,1)) * glm.vec4(dir, 0))
                #dir *= min(1, dt*10.)
                sum_dir += dir
                num += 1
        if num:
            self.world.agents["player"].move(sum_dir / num * 1.5)

        if self.keys[pyglet.window.key.SPACE]:
            self.world.agents["player"].jump()

    def on_draw(self):
        self.clear()
        self.world.render(time.time() - self.start_time)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.world.projection._rotation[0] -= scroll_y / 30.

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.world.projection._rotation[1] += dx / 30.

    def on_mouse_press(self, x, y, button, modifiers):
        import random
        ro, rd = self.get_ray(x, y)
        t, hit = self.world.chunk.cast_voxel_ray(ro, rd, 1000)
        if hit:
            pos = glm.floor(ro + t * rd)
            self.world.click_voxel = pos
            ihit = tuple(int(x) for x in pos)
            self.world.agents.set_goal("player", ihit)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.close()
        elif symbol == pyglet.window.key.F4:
            self.world.edit_mode = not self.world.edit_mode

    def on_text(self, text):
        if text in self.world.projection.PROJECTIONS:
            self.world.projection.init(text)
        if text == "f":
            self.set_fullscreen(not self.fullscreen)
        if text == "+":
            self.world.projection.zoom += 1.
        if text == "-":
            self.world.projection.zoom -= 1.
        if text == "d":
            self.world.debug_view = (self.world.debug_view + 1) % 3
        if text == ".":
            OpenGlAssets.dump()

    def get_ray(self, x, y):
        return self.world.projection.screen_to_ray(x, y)

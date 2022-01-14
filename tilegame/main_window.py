import time
import traceback

import glm
import pyglet

from lib.opengl import *
from lib.opengl.core.base import OpenGlObjects

from .game import Game
from .render.renderer import GameRenderer


class MainWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            width=1024, height=768,
            vsync=True,
            **kwargs
        )
        self.game = Game()
        self.renderer = GameRenderer(self.game)

        self.keys = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keys)

        # time(r)
        self.start_time = time.time()
        pyglet.clock.schedule_interval(self.update, 1.0 / 60.0)
        # pyglet.clock.set_fps_limit(60)

    def time(self) -> float:
        return time.time() - self.start_time

    def update(self, dt: float):
        self.game.check_keys(self.keys, dt)
        self.game.update(time, dt)
        self.renderer.update(time, dt)

    def on_draw(self):
        try:
            self.renderer.render_settings.set_size(self.width, self.height)
            self.renderer.render_settings.time = self.time()

            self.clear()
            self.renderer.render()
        except Exception as e:
            traceback.print_exc()
            exit(-1)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.close()

    def on_text(self, text):
        if text == ".":
            OpenGlObjects.dump()
            OpenGlAssets.dump()
        if text == "f":
            self.set_fullscreen(not self.fullscreen)

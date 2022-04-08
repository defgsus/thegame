import time
import traceback

import glm
import pyglet

from lib.opengl import *
from lib.opengl.core.base import OpenGlObjects
from lib.gen import Worker

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

        self.start_time = time.time()
        pyglet.clock.schedule_interval(self.update, 1.0 / 60.0)
        # pyglet.clock.set_fps_limit(60)

    def close(self):
        Worker.stop_all()
        super().close()

    def time(self) -> float:
        return time.time() - self.start_time

    def update(self, dt: float):
        time = self.time()
        self.game.render_settings = self.renderer.render_settings
        self.check_keys(dt)
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
            self.close()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_key_press(self, symbol, modifiers):
        try:
            if symbol == pyglet.window.key.ESCAPE:
                self.close()
            else:
                self.game.on_key_press(symbol, modifiers)
        except:
            traceback.print_exc()
            self.close()

    def on_text(self, text):
        if text == ".":
            print("-- opengl objects --")
            OpenGlObjects.dump()
            print("-- opengl assets --")
            OpenGlAssets.dump()
            print("-- object map --")
            self.game.world.objects.dump_object_map()
        elif text == "f":
            self.set_fullscreen(not self.fullscreen)

    def check_keys(self, dt: float):
        if self.keys[pyglet.window.key.MINUS]:
            self.renderer.render_settings.projection.scale *= min(1.1, 1. + dt)
        if self.keys[pyglet.window.key.PLUS]:
            self.renderer.render_settings.projection.scale *= max(.9, 1. - dt)

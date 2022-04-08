import math

import glm
import pyglet

from .render.rs import GameRenderSettings
from .world import World


class Game:

    def __init__(self):
        self.world = World()
        # will be replaced by mainwindow
        self.render_settings = GameRenderSettings(32, 32)

    @property
    def player(self):
        return self.world.player

    def check_keys(self, keys: dict, dt: float):
        dir_mapping = {
            pyglet.window.key.UP: [0, .1],
            pyglet.window.key.DOWN: [0, -.1],
            pyglet.window.key.LEFT: [-.1, 0],
            pyglet.window.key.RIGHT: [.1, 0],
        }
        for key, d in dir_mapping.items():
            if keys.get(key):
                self.player.body.position = (
                    self.player.position[0] + d[0],
                    self.player.position[1] + d[1],
                )

    def on_key_press(self, symbol, modifiers):
        pass

    def update(self, time: float, dt: float):
        self.world.update(time, dt)

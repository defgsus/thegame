import math

import glm
import pyglet

from .map.tilemap import TilemapSampler
from .render.rs import GameRenderSettings


class Game:

    def __init__(self):
        self.tile_map = TilemapSampler()
        self.player_pos = glm.vec2(0, 0)
        self.player_rotation = 0.
        # replaced by mainwindow
        self.render_settings = GameRenderSettings(32, 32)

    def check_keys(self, keys: dict, dt: float):
        speed = min(1., dt * 5.)
        dir_mapping = {
            pyglet.window.key.LEFT: -1,
            pyglet.window.key.RIGHT: 1,
        }
        for key, dir in dir_mapping.items():
            if keys.get(key):
                self.player_rotation -= speed * dir * 30.

        dir_mapping = {
            pyglet.window.key.UP: 1,
            pyglet.window.key.DOWN: -1,
        }
        a = self.player_rotation / 180. * math.pi
        norm = glm.vec2(-math.sin(a), math.cos(a))
        for key, dir in dir_mapping.items():
            if keys.get(key):
                self.player_pos += dir * speed * (1. + self.render_settings.projection.scale / 10.) * norm

    def on_key_press(self, symbol, modifiers):
        pass

    def update(self, time: float, dt: float):
        pass

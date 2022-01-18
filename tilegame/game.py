import math

import glm
import pyglet

from .map.tilemap import TilemapSampler
from .render.rs import GameRenderSettings
from .objects import WalkerObject


class Game:

    def __init__(self):
        self.tile_map = TilemapSampler()
        self.player = WalkerObject("player")
        # will be replaced by mainwindow
        self.render_settings = GameRenderSettings(32, 32)

    def check_keys(self, keys: dict, dt: float):
        speed = min(1., dt)
        dir_mapping = {
            pyglet.window.key.LEFT: -1,
            pyglet.window.key.RIGHT: 1,
        }
        for key, dir in dir_mapping.items():
            if keys.get(key):
                self.player.turn(speed * dir)

        dir_mapping = {
            pyglet.window.key.UP: 1,
            pyglet.window.key.DOWN: -1,
        }
        scale = (1. + self.render_settings.projection.scale / 10.)
        for key, dir in dir_mapping.items():
            if keys.get(key):
                self.player.walk(speed * dir * scale)

    def on_key_press(self, symbol, modifiers):
        pass

    def update(self, time: float, dt: float):
        self.player.update(time, dt)

import math

import glm
import pyglet

from .render.rs import GameRenderSettings
from .objects import WalkerObject
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
        self.world.update(time, dt)

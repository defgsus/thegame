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
        self.player.controller.check_keys(keys, dt)

    def on_key_press(self, symbol, modifiers):
        pass

    def update(self, time: float, dt: float):
        self.world.update(time, dt)

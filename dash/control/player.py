from typing import Tuple

import pyglet

from .base import ControllerBase
from ..map import Object


class PlayerBugController(ControllerBase):

    def __init__(self, obj: Object):
        super().__init__()
        self.add_object(obj)

    def check_keys(self, keys: dict, dt: float):
        dir_mapping = {
            pyglet.window.key.UP: (0, 1),
            pyglet.window.key.DOWN: (0, -1),
            pyglet.window.key.LEFT: (-1, 0),
            pyglet.window.key.RIGHT: (1, 0),
        }
        for key, delta in dir_mapping.items():
            if keys.get(key):
                self.objects[0].apply_impulse(delta)

    def update(self, time: float, dt: float):
        pass

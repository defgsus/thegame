from typing import List

import pymunk

from ..map import Object


class ControllerBase:

    def __init__(self):
        self.objects: List[Object] = []
        self.space: pymunk.Space = None

    def add_object(self, obj: Object):
        self.objects.append(obj)
        if self.space is None:
            self.space = obj.space

    def update(self, time: float, dt: float):
        pass


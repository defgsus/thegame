from .core.base import *


class RenderNode:

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self.name)

    def num_color_textures(self):
        return 1

    def has_depth_texture(self):
        return False

    def num_multi_sample(self):
        return 0
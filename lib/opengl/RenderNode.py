from .core.base import *


class RenderNode:

    def __init__(self, name):
        self.name = name
        self.is_created = False

    def __str__(self):
        return "%s('%s', created=%s, numcol=%s)" % (
            self.__class__.__name__,
            self.name, self.is_created, self.num_color_outputs(),
        )

    def num_color_outputs(self):
        return 1

    def has_depth_output(self):
        return False

    def num_multi_sample(self):
        return 0

    def output_slots(self):
        s = list(range(self.num_color_outputs()))
        if self.has_depth_output():
            s.append("depth")
        return s

    def create(self, render_settings):
        pass

    def release(self):
        pass

    def render(self, render_settings):
        raise NotImplementedError

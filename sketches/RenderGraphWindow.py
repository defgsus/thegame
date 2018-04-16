import pyglet

from lib.opengl import *


class RenderGraphWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(RenderGraphWindow, self).__init__(*args, **kwargs)
        self.graph = RenderGraph()

        self.pipeline = self.graph.create_pipeline()

    def on_draw(self):
        self.clear()

        self.pipeline.draw()


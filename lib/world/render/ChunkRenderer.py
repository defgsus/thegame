import time
import pyglet
import glm
import math
from ...opengl import *
from ...opengl import postproc
from .ChunkMeshRenderNode import ChunkMeshRenderNode


class ChunkRenderer:

    def __init__(self, world):
        self.world = world
        self.render_settings = world.render_settings
        self.asset_id = "level01"

        self.render_graph = RenderGraph()

        self.render_graph.add_node(ChunkMeshRenderNode(self.world, self, "mesh"))
        #self.render_graph.add_node(postproc.Desaturate("post"))

        #self.render_graph.connect("mesh", 0, "post", 0)

        self.pipeline = self.render_graph.create_pipeline()

    def render(self):
        self.pipeline.render(self.render_settings)
        self.pipeline.render_to_screen(self.render_settings)
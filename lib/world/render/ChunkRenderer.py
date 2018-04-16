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
        self.pp_depth_blur = postproc.Blur("depth-blur", use_mask=True)
        self.render_graph.add_node(self.pp_depth_blur)

        self.render_graph.connect("mesh", 0, "depth-blur", 0)
        self.render_graph.connect("mesh", "depth", "depth-blur", 1)

        self.pipeline = self.render_graph.create_pipeline()

    def render(self):
        self.pp_depth_blur.mask_center, self.pp_depth_blur.mask_spread = self.render_settings.projection.get_depth_mask_values()
        self.pipeline.render(self.render_settings)
        self.pipeline.render_to_screen(self.render_settings)
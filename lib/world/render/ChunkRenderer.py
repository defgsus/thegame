import time
import pyglet
import glm
import math
from ...opengl import *
from ...opengl import postproc
from .ChunkMeshRenderNode import ChunkMeshRenderNode
from .ChunkMeshLightingNode import ChunkMeshLightingNode
from .ChunkMeshAllNode import ChunkMeshAllNode

"""
some benchmarks:
    480 x 320 on GTX 1050
        Mesh with Lighting
            smooth shadow
                no MSAA 444 fps
                16xMSAA 196 fps (213fps backface culling)
            voxel shadow
                no MSAA 580 fps
                16xMSAA 300 fps (320fps backface culling)
            no shadow
                no MSAA 725 fps
                16xMSAA 350 fps
        deferred lighting
            smooth shadow
                16xMSAA 148 fps
"""


class ChunkRenderer:

    def __init__(self, world):
        self.world = world
        self.render_settings = world.render_settings
        self.asset_id = "level01"

        self.render_graph = RenderGraph()

        if 0:
            self.render_graph.add_node(ChunkMeshRenderNode(self.world, self, "mesh"))
            self.render_graph.add_node(ChunkMeshLightingNode(self.world, self, "light"))

            self.render_graph.connect("mesh", 0, "light", 0)
            self.render_graph.connect("mesh", 1, "light", 1)
            self.render_graph.connect("mesh", 2, "light", 2)

            self.pp_depth_blur = self.render_graph.add_node(postproc.Blur("depth-blur", use_mask=True))

            self.render_graph.connect("light", 0, "depth-blur", 0)
            self.render_graph.connect("mesh", "depth", "depth-blur", 1)
        else:
            self.render_graph.add_node(ChunkMeshAllNode(self.world, self, "mesh"))
            self.pp_depth_blur = self.render_graph.add_node(postproc.Blur("depth-blur", use_mask=True))
            self.render_graph.connect("mesh", 0, "depth-blur", 0)
            self.render_graph.connect("mesh", "depth", "depth-blur", 1)

        self.pipeline = self.render_graph.create_pipeline()

    def render(self):
        if hasattr(self, "pp_depth_blur"):
            (self.pp_depth_blur.mask_center,
             self.pp_depth_blur.mask_spread) = self.render_settings.projection.get_depth_mask_values()
        self.pipeline.render(self.render_settings)
        self.pipeline.render_to_screen(self.render_settings)
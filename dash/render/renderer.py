import time
import math
from typing import Optional

from pyglet import gl
import glm

from lib.opengl import *
from lib.math import FollowFilter
from .._path import ASSET_PATH
from ..game import Game
from .rs import GameRenderSettings
from .tilemap_node import TileMapNode


class GameRenderer:

    def __init__(self, game: Game):
        self.game = game
        self.graph: Optional[RenderGraph] = None
        self.pipeline: Optional[RenderPipeline] = None
        self.render_settings = GameRenderSettings(32, 32)
        self.frame_number = 0
        self.camera_pos = glm.vec2(-1, -5)
        self.camera_rotation = 0.
        self._target_speed_filter = FollowFilter(follow_up=.03, follow_down=.01)

    def update(self, time: float, dt: float):
        target = self.game.player
        #target_speed = self._target_speed_filter(target.average_speed)
        target_pos = glm.vec2(target.pos) #+ target.direction_of_movement * target_speed * .5
        self.camera_pos += min(1., dt * 3.) * (target_pos - self.camera_pos)
        # self.camera_rotation += min(1., dt*.3) * (self.game.player.rotation - self.camera_rotation)
        self.pipeline.update(self.render_settings, dt)

    def render(self):
        self.render_settings.projection.location = self.camera_pos
        self.render_settings.projection.rotation_deg = self.camera_rotation

        if self.graph is None:
            self.graph = self.create_render_graph()

        if self.pipeline is None:
            self.pipeline = self.graph.create_pipeline()
            self.pipeline.dump()
            # self.pipeline.verbose = 5

        #if self.frame_number % 100 == 0:
        #    self.tile_render_node.upload_map(self.game.tile_map.get_map(0, 0, 32, 32))
        self.pipeline.render(self.render_settings)
        self.pipeline.render_to_screen(self.render_settings)
        self.frame_number += 1

    def create_render_graph(self) -> RenderGraph:
        graph = RenderGraph()

        tile_tex = Texture2DNode(
            ASSET_PATH /
            "tileset01.png"
        )
        graph.add_node(tile_tex)

        self.tile_render_node = TileMapNode("tilerender", self.game.world.tile_map)
        graph.add_node(self.tile_render_node)

        graph.connect(tile_tex, 0, self.tile_render_node, mag_filter=gl.GL_NEAREST)

        return graph

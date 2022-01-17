from functools import partial
from typing import Optional, Dict

import glm
import numpy as np

from lib.opengl.core.base import *
from lib.opengl import *
from lib.gen import Worker
from lib.geom import *

from .shader_node import GameShaderNode
from .rs import GameRenderSettings
from ..map import TilemapSampler
from ..game import Game
from tests.util import Timer


class ObjectNode(RenderNode):

    def __init__(self, game: Game, name: str = "objects"):
        super().__init__(name)
        self.game = game
        self.mesh: Optional[TriangleMesh] = None
        self.drawable: Optional[Drawable] = None
        self._create_mesh()
        self.drawable = self.mesh.create_drawable(f"{self.name}-mesh")

    def num_multi_sample(self) -> int:
        return 4

    def create(self, render_settings: RenderSettings):
        pass

    def release(self):
        self.drawable.release()

    def render(self, rs: GameRenderSettings, pass_num: int):
        proj = rs.projection.projection_matrix_4()
        trans = rs.projection.transformation_matrix_4()

        trans *= glm.translate(glm.mat4(1), glm.vec3(self.game.player_pos, 0))
        trans *= glm.rotate(glm.mat4(1), self.game.player_rotation / 180 * glm.pi(), glm.vec3(0, 0, 1))

        self.drawable.shader.set_uniform("u_projection", proj)
        self.drawable.shader.set_uniform("u_transformation", trans)
        self.drawable.draw()

    def _create_mesh(self):
        self.mesh = TriangleMesh()
        factory = MeshFactory()
        factory.add_icosahedron(self.mesh)

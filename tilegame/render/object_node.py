from functools import partial
from typing import Optional, Dict

import glm
import numpy as np

from lib.opengl.core.base import *
from lib.opengl import *
from lib.gen import Worker
from lib.geom import *

from .rs import GameRenderSettings
from .mesh_object import MeshObject
from ..game import Game
from tests.util import Timer


class ObjectNode(RenderNode):

    def __init__(self, game: Game, name: str = "objects"):
        super().__init__(name)
        self.game = game
        self.mesh = MeshObject(2)

    def num_multi_sample(self) -> int:
        return 4

    def create(self, render_settings: RenderSettings):
        pass

    def release(self):
        self.mesh.release()

    def render(self, rs: GameRenderSettings, pass_num: int):
        # print(self.drawable._attributes["a_position"])

        proj = rs.projection.projection_matrix_4()
        trans = rs.projection.transformation_matrix_4()

        trans *= glm.translate(glm.mat4(1), glm.vec3(self.game.player_pos, 0))
        trans *= glm.rotate(glm.mat4(1), self.game.player_rotation / 180 * glm.pi(), glm.vec3(0, 0, 1))

        #trans *= glm.rotate(glm.mat4(1), rs.time / 2., glm.vec3(0.707, 0.707, 0))

        self.mesh.render(
            projection=proj,
            transformation=trans,
        )
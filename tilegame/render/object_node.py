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
from ..objects import ObjectBase
from tests.util import Timer


class ObjectNode(RenderNode):

    def __init__(self, object: ObjectBase, name: Optional[str] = None):
        super().__init__(name or object.id)
        self.object = object
        self.mesh = self.object.create_mesh()

    def num_multi_sample(self) -> int:
        return 4

    def has_depth_output(self) -> bool:
        return True

    def create(self, render_settings: RenderSettings):
        pass

    def release(self):
        self.mesh.release()

    def update(self, rs: RenderSettings, dt: float):
        self.object.update_mesh(self.mesh, rs.time, dt)

    def render(self, rs: GameRenderSettings, pass_num: int):
        # print(self.drawable._attributes["a_position"])

        proj = rs.projection.projection_matrix_4()
        trans = rs.projection.transformation_matrix_4()

        trans *= self.object.transformation_matrix()

        self.mesh.render(
            projection=proj,
            transformation=trans,
        )
from typing import Optional, Dict, Tuple

import glm
import numpy as np
import pymunk

from lib.opengl.core.base import *
from lib.opengl import *
from lib.geom import LineMesh

from .shader_node import GameShaderNode
from .rs import GameRenderSettings
from ..map import Objects, Object


class ConstraintDebugNode(GameShaderNode):

    def __init__(
            self,
            name: str,
            object_map: Objects,
    ):
        super().__init__(name)
        self.object_map = object_map

        self.drawable = Drawable(f"{name}-drawable")

    def create(self, render_settings: GameRenderSettings):
        super().create(render_settings)

    def release(self):
        self.drawable.release()
        super().release()

    def render(self, rs: GameRenderSettings, pass_num: int):
        self.drawable.shader.set_uniform("u_projection", rs.projection.projection_matrix_4())
        self.drawable.shader.set_uniform("u_transformation", rs.projection.transformation_matrix_4())

        mesh = self.build_constraint_mesh()

        # print("X", mesh.vertices_array())
        if not mesh.is_empty():
            mesh.update_drawable(self.drawable)

        if not self.drawable.is_empty():
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            self.drawable.draw()

    def build_constraint_mesh(self) -> LineMesh:
        mesh = LineMesh()
        mesh.set_color(1, 1, 1, 1)
        for c in self.object_map.space.constraints:
            if hasattr(c, "anchor_a"):
                pos_a = c.a.local_to_world(c.anchor_a)
                pos_b = c.b.local_to_world(c.anchor_b)
                mesh.add_line((pos_a[0], pos_a[1], 0), (pos_b[0], pos_b[1], 0))
            else:
                pos_a = c.a.position
                pos_b = c.b.position
                mesh.add_line((pos_a[0], pos_a[1], 0), (pos_b[0], pos_b[1], 0))

        return mesh

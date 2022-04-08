from typing import Optional, Dict, Tuple

import glm
import numpy as np
import pymunk

from lib.opengl.core.base import *
from lib.opengl import *
from lib.geom import MeshFactory, TriangleMesh

from .shader_node import GameShaderNode
from .rs import GameRenderSettings
from ..map import ObjectMap, Object


class ObjectDebugNode(GameShaderNode):

    def __init__(
            self,
            name: str,
            object_map: ObjectMap,
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

        mesh = self.build_object_mesh()

        # print("X", mesh.vertices_array())
        if not mesh.is_empty():
            mesh.update_drawable(self.drawable)

        if not self.drawable.is_empty():
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            self.drawable.draw()

    def build_object_mesh(self) -> TriangleMesh:
        mesh = TriangleMesh()
        mesh.create_attribute("a_color", 4, (1, 1, 1, .9))
        #mesh.set_attribute_value("a_color", (1, 1, 1, .5))
        for o in self.object_map.static_objects.values():
            o.add_to_mesh(mesh)

        for o in self.object_map.objects:
            o.add_to_mesh(mesh)

        return mesh

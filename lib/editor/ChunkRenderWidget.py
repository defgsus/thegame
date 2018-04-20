import glm

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtOpenGL import *

from lib.opengl import *
from lib.world.render import RenderSettings
from .render.ChunkMeshNode import ChunkMeshNode


class ChunkRenderWidget(QGLWidget):

    def __init__(self, chunk, parent):
        super().__init__(parent)

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

        self.edit_id = "%s" % id(self)
        self.chunk = chunk
        self.render_settings = RenderSettings(480, 320)
        self.graph = RenderGraph()
        self.mesh_node = self.graph.add_node(ChunkMeshNode(self.edit_id, chunk, "chunk-mesh"))
        self.pipeline = self.graph.create_pipeline()
        self.view_center = glm.vec3(0)

        self.update_projection()

    def update_projection(self):
        self.render_settings.projection.user_transformation = glm.translate(
            glm.mat4(1), -glm.vec3(self.view_center)-.5)
        self.render_settings.projection.update(1)
        self.update()

    def get_ray(self, x, y):
        return self.render_settings.screen_to_ray(x, self.height()-1-y)

    def mouseMoveEvent(self, e):
        ro, rd = self.get_ray(e.x(), e.y())
        t, hit = self.chunk.cast_voxel_ray(ro, rd, 300)
        if hit:
            hit_voxel = tuple(int(x) for x in (ro+t*rd)) if hit else (-1,-1,-1)
            #print(hit, t, hit_voxel)
        else:
            hit_voxel = None
        if self.mesh_node.focus_voxel != hit_voxel:
            self.mesh_node.focus_voxel = hit_voxel
            self.update()

    def mousePressEvent(self, e):
        pass
        #if self.mesh_node.focus_voxel:
        #    self.update_projection()

    def keyPressEvent(self, e):
        move_dir = None
        if e.key() == Qt.Key_Left:
            move_dir = (-1,0,0)
        elif e.key() == Qt.Key_Right:
            move_dir = (1,0,0)
        elif e.key() == Qt.Key_Up:
            move_dir = (0,1,0)
        elif e.key() == Qt.Key_Down:
            move_dir = (0,-1,0)

        if move_dir is None:
            super().keyPressEvent(e)
        else:
            move_dir = self.render_settings.projection.get_direction(move_dir)
            move_dir.z = 0
            self.view_center += move_dir
            self.update_projection()

    def initializeGL(self):
        pass

    def resizeGL(self, w, h):
        pass

    def paintGL(self):
        self.render_settings.screen_width = self.width()
        self.render_settings.screen_height = self.height()

        self.pipeline.render(self.render_settings)
        self.pipeline.render_to_screen(self.render_settings)

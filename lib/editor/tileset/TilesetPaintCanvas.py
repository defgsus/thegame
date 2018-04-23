from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class TilesetPaintCanvas(QWidget):

    def __init__(self, tileset, parent):
        super().__init__(parent)

        self.setMouseTracking(True)

        self.tileset = tileset
        self.qimage = tileset.get_qimage()

        self.grid_pen = QPen()
        self.grid_pen.setColor(QColor(255, 127, 0))
        self.grid_pen.setWidthF(.2)

        self._zoom = 10

        self._apply_transform()

        self.hover_pos = QPoint(0, 0)

    @property
    def transform(self):
        return self._transform

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, z):
        self._zoom = z
        self._apply_transform()

    @property
    def brush_radius(self):
        return 2

    def _apply_transform(self):
        self._transform = QTransform()
        self._transform.scale(self._zoom, self._zoom)
        self._itransform, __ = self._transform.inverted()
        print(self._itransform)
        size = QPointF(self.tileset.image_width, self.tileset.image_height)
        size = self._transform.map(size)
        self.setFixedSize(int(size.x()), int(size.y()))

    def paintEvent(self, e):
        p = QPainter(self)
        p.setTransform(self._transform)

        p.drawImage(0, 0, self.qimage)

        # update rect in pixel coords
        urect = e.rect()
        urect = QRect(self._itransform.map(urect.topLeft()), self._itransform.map(urect.bottomRight()))

        # -- grid --

        p.setPen(self.grid_pen)
        grid_from = (urect.left() // self.tileset.tile_width - 1) * self.tileset.tile_width
        grid_to = (urect.right() // self.tileset.tile_width + 1) * self.tileset.tile_width
        for i in range(grid_from, grid_to+1, self.tileset.tile_width):
            p.drawLine(i, urect.top()-self.zoom, i, urect.bottom()+self.zoom)

        grid_from = (urect.top() // self.tileset.tile_height - 1) * self.tileset.tile_height
        grid_to = (urect.bottom() // self.tileset.tile_height + 1) * self.tileset.tile_height
        for i in range(grid_from, grid_to+1, self.tileset.tile_height):
            p.drawLine(urect.left()-self.zoom, i, urect.right()+self.zoom, i)

        # hover pos
        p.drawEllipse(self.hover_pos, 2, 2)

        #p.drawRect(urect)

    def mouseMoveEvent(self, e):
        prev_hover_pos = self.hover_pos
        self.hover_pos = self._itransform.map(e.pos())
        p = self._transform.map(self.hover_pos)
        urect = QRect(p, p)
        p = self._transform.map(prev_hover_pos)
        urect = urect.united(QRect(p, p))
        s = (self.brush_radius+1) * self.zoom
        urect.adjust(-s, -s, s, s)
        self.update(urect)

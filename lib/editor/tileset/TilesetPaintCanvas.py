from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .Brush import Brush


class TilesetPaintCanvas(QWidget):

    selectedTileChanged = pyqtSignal(QRect)
    imageChanged = pyqtSignal()

    def __init__(self, tileset, brush, parent):
        super().__init__(parent)

        self.setMouseTracking(True)

        self.tileset = tileset
        self.qimage = tileset.get_qimage()
        self.brush = brush
        self.clip_rect = None
        self.hover_pos = QPoint(0, 0)
        self.prev_hover_pos = QPoint(0, 0)

        self._create_pens()
    
        self._zoom = 10
        self._apply_transform()

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

    def _apply_transform(self):
        self._transform = QTransform()
        self._transform.scale(self._zoom, self._zoom)
        self._itransform, __ = self._transform.inverted()
        size = QPointF(self.tileset.image_width, self.tileset.image_height)
        size = self._transform.map(size)
        self.setFixedSize(int(size.x()), int(size.y()))

    def paintEvent(self, e):
        p = QPainter(self)
        p.setTransform(self._transform)

        # update-rect in pixel coords
        urect = e.rect()
        urect = QRect(self._itransform.map(urect.topLeft()), self._itransform.map(urect.bottomRight()))

        # -- background --
        p.setPen(Qt.NoPen)
        p.setBrush(self.back_brush1)
        p.drawRect(0,0, self.qimage.width(), self.qimage.height())
        p.setBrush(self.back_brush2)
        p.drawRect(0,0, self.qimage.width(), self.qimage.height())

        # -- actual image --
        p.drawImage(0, 0, self.qimage)

        # -- grid --

        p.setBrush(Qt.NoBrush)
        p.setPen(self.grid_pen)
        grid_from = (urect.left() // self.tileset.tile_width - 1) * self.tileset.tile_width
        grid_to = (urect.right() // self.tileset.tile_width + 1) * self.tileset.tile_width
        for i in range(grid_from, grid_to+1, self.tileset.tile_width):
            p.drawLine(i, urect.top()-self.zoom, i, urect.bottom()+self.zoom)

        grid_from = (urect.top() // self.tileset.tile_height - 1) * self.tileset.tile_height
        grid_to = (urect.bottom() // self.tileset.tile_height + 1) * self.tileset.tile_height
        for i in range(grid_from, grid_to+1, self.tileset.tile_height):
            p.drawLine(urect.left()-self.zoom, i, urect.right()+self.zoom, i)

        # -- hover pos --
        p.setPen(self.hover_pen)
        if self.brush.is_brush() or self.brush.mode == "swipe":
            p.drawEllipse(self.hover_pos+QPointF(.5,.5), self.brush.radius-.5, self.brush.radius-.5)
        else:
            p.drawLine(self.hover_pos+QPointF(.5,0), self.hover_pos+QPointF(.5,1))
            p.drawLine(self.hover_pos+QPointF(0,.5), self.hover_pos+QPointF(1,.5))

        #p.drawRect(urect)

    def screen_to_pixel(self, pos):
        p = self._itransform.map(QPointF(pos))
        p = p - QPointF(.501, .501)
        return p.toPoint()

    def get_clip_rect(self, pixel_pos):
        return QRect(
            (pixel_pos.x() // self.tileset.tile_width) * self.tileset.tile_width,
            (pixel_pos.y() // self.tileset.tile_height) * self.tileset.tile_height,
            self.tileset.tile_width,
            self.tileset.tile_height
        )

    def get_tile_qimage(self, rect=None):
        if rect is None:
            rect = self.clip_rect
        return self.qimage.copy(rect)

    def mousePressEvent(self, e):
        prev_clip_rect = self.clip_rect

        if e.button() == Qt.LeftButton:
            e.accept()
            self.hover_pos = self.screen_to_pixel(e.pos())
            self.clip_rect = self.get_clip_rect(self.hover_pos)
            if self.brush.is_draw_tool():
                if not self.brush.mode == "swipe":
                    self.draw_brush(self.hover_pos)
            self._update_pixels(self.hover_pos, None, self.brush.radius)

        if prev_clip_rect != self.clip_rect:
            self.selectedTileChanged.emit(self.clip_rect)

    def mouseReleaseEvent(self, e):
        self.clip_rect = None

    def mouseMoveEvent(self, e):
        self.hover_pos = self.screen_to_pixel(e.pos())
        if e.buttons() & Qt.LeftButton:
            e.accept()
            if self.hover_pos != self.prev_hover_pos:
                if self.brush.is_brush():
                    self.draw_brush(self.hover_pos)
                elif self.brush.mode == "swipe":
                    self.draw_brush(self.hover_pos)
        self._update_pixels(self.prev_hover_pos, self.hover_pos, self.brush.radius)
        self.prev_hover_pos = self.hover_pos

    def draw_brush(self, pos):
        if self.brush.is_brush():
            self.brush.draw(pos, self.qimage, self.clip_rect)
        elif self.brush.mode == "fill":
            self.brush.flood_fill(pos, self.qimage, self.clip_rect)
            self.update()
        elif self.brush.mode == "swipe":
            self.brush.swipe(self.prev_hover_pos, pos, self.qimage, self.clip_rect)
        else:
            return
        self.imageChanged.emit()

    def _update_pixels(self, p1, p2, radius):
        p = self._transform.map(p1)
        urect = QRect(p, p)
        if p2 is not None:
            p = self._transform.map(p2)
            urect = urect.united(QRect(p, p))
        s = (radius+2) * self.zoom
        urect.adjust(-s, -s, s, s)
        self.update(urect)

    def _create_pens(self):
        self.back_brush1 = QBrush(QColor(128,128,128))
        self.back_brush2 = QBrush(QColor(230,230,230))
        self.back_brush2.setStyle(Qt.Dense2Pattern)

        self.grid_pen = QPen()
        self.grid_pen.setColor(QColor(255, 127, 0, 127))
        self.grid_pen.setWidthF(.2)

        self.hover_pen = QPen()
        self.hover_pen.setColor(QColor(0, 0, 0, 127))
        self.hover_pen.setWidthF(.2)

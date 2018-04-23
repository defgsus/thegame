import math
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Brush:

    MODE_REPLACE = 1
    MODE_ADD = 2

    def __init__(self):
        self.mode = self.MODE_ADD
        self._radius = 2
        self._color = QColor(0,255,255,30)
        self._brush = None
        self._update_brush_image()

    @property
    def radius(self):
        return self._radius

    @property
    def color(self):
        return self._color

    def set_radius(self, r):
        self._radius = int(r)
        self._update_brush_image()

    def draw(self, pos, qimage):
        r = self._radius - .5
        if self.mode == self.MODE_ADD:
            center = pos - QPointF(r, r)
            p = QPainter(qimage)
            p.drawImage(center, self._brush)
        elif self.mode == self.MODE_REPLACE:
            # TODO
            qimage.setPixel(pos, self.color.rgba())

    def _update_brush_image(self):
        self._brush = QImage((self._radius-1)*2+1, (self._radius-1)*2+1, QImage.Format_RGBA8888)
        cx = self._brush.width() / 2 - .5
        cy = self._brush.height() / 2 - .5
        for y in range(self._brush.height()):
            for x in range(self._brush.width()):
                dx, dy = cx-x, cy-y
                d = math.sqrt(dx*dx + dy*dy)
                col = QColor(self._color)
                col.setAlphaF(max(0., 1.- d / self.radius) * col.alphaF())
                self._brush.setPixel(x, y, col.rgba())

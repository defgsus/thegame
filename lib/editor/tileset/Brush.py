import math
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Brush:

    MODES = {
        "add": QPainter.CompositionMode_SourceOver,
        "replace": QPainter.CompositionMode_Source,
        "multiply": QPainter.CompositionMode_Multiply,
        "lighten": QPainter.CompositionMode_Lighten,
        "darken": QPainter.CompositionMode_Lighten,
        "difference": QPainter.CompositionMode_Difference,
    }

    def __init__(self):
        self.mode = "add"
        self._radius = 2
        self._color = QColor(255,255,255)
        self._alpha = 255
        self._brush = None
        self._update_brush_image()

    @property
    def radius(self):
        return self._radius

    @property
    def color(self):
        return self._color

    @property
    def alpha(self):
        return self._alpha

    def set_radius(self, r):
        self._radius = int(r)
        self._update_brush_image()

    def set_mode(self, m):
        self.mode = m

    def set_color(self, c):
        self._color = c
        self._update_brush_image()

    def set_alpha(self, a):
        self._alpha = max(0, min(255, a))
        self._update_brush_image()

    def draw(self, pos, qimage, clip_rect=None):
        r = self._radius - .5
        center = pos - QPointF(r, r)
        p = QPainter(qimage)
        if clip_rect is not None:
            p.setClipRect(clip_rect)
        p.setCompositionMode(self.MODES[self.mode])

        p.drawImage(center, self._brush)

    def _update_brush_image(self):
        self._brush = QImage((self._radius-1)*2+1, (self._radius-1)*2+1, QImage.Format_RGBA8888)
        cx = self._brush.width() / 2 - .5
        cy = self._brush.height() / 2 - .5
        alpha = self.alpha / 255.
        for y in range(self._brush.height()):
            for x in range(self._brush.width()):
                dx, dy = cx-x, cy-y
                d = math.sqrt(dx*dx + dy*dy)
                col = QColor(self._color)
                col.setAlphaF(alpha * max(0., 1.- d / self.radius) * col.alphaF())
                self._brush.setPixel(x, y, col.rgba())

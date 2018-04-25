import math
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Brush:

    DRAW_MODES = {
        "add": QPainter.CompositionMode_SourceOver,
        "replace": QPainter.CompositionMode_Source,
        "multiply": QPainter.CompositionMode_Multiply,
        "light(soft)": QPainter.CompositionMode_SoftLight,
        "light(hard)": QPainter.CompositionMode_HardLight,
        #"lighten": QPainter.CompositionMode_Lighten,
        #"darken": QPainter.CompositionMode_Lighten,
        "difference": QPainter.CompositionMode_Difference,
    }

    DRAW_TOOLS = {
        "fill",
        "swipe",
    }

    def __init__(self):
        self.mode = "select"
        self.fill_tolerance = 0
        self._radius = 2
        self._color = QColor(255, 255, 255)
        self._alpha = 255
        self._brush = None
        self._brush_qimage = None

    @property
    def radius(self):
        return self._radius

    @property
    def color(self):
        return self._color

    @property
    def alpha(self):
        return self._alpha

    def is_brush(self):
        return self.mode in self.DRAW_MODES

    def is_draw_tool(self):
        return self.mode in self.DRAW_MODES or self.mode in self.DRAW_TOOLS

    def set_radius(self, r):
        self._radius = int(r)
        self._brush_qimage = None

    def set_mode(self, m):
        self.mode = m

    def set_color(self, c):
        self._color = c
        self._brush_qimage = None

    def set_alpha(self, a):
        self._alpha = max(0, min(255, a))
        self._brush_qimage = None

    def set_fill_tolerance(self, t):
        self.fill_tolerance = t

    def draw(self, pos, qimage, clip_rect=None):
        assert self.mode in self.DRAW_MODES

        r = self._radius - .5
        center = pos - QPointF(r, r)
        p = QPainter(qimage)
        if clip_rect is not None:
            p.setClipRect(clip_rect)
        p.setCompositionMode(self.DRAW_MODES[self.mode])

        p.drawImage(center, self.brush_image)

    def swipe(self, pos1, pos2, qimage, clip_rect=None):
        src = QImage(self.radius*2+1, self.radius*2+1, QImage.Format_RGBA8888)
        cx = src.width() / 2 - .5
        cy = src.height() / 2 - .5
        srcx = pos1.x() - self.radius
        srcy = pos1.y() - self.radius
        alpha = self.alpha / 255.
        for y in range(src.height()):
            sy = max(0, min(qimage.height()-1, srcy + y))
            if clip_rect is not None:
                if sy < clip_rect.top():
                    sy = clip_rect.top()
                if sy > clip_rect.bottom():
                    sy = clip_rect.bottom()
            for x in range(src.width()):
                sx = max(0, min(qimage.width()-1, srcx + x))
                if clip_rect is not None:
                    if sx < clip_rect.left():
                        sx = clip_rect.left()
                    if sx > clip_rect.right():
                        sx = clip_rect.right()
                dx, dy = cx-x, cy-y
                d = math.sqrt(dx*dx + dy*dy)
                col = QColor(qimage.pixel(sx, sy))
                col.setAlphaF(alpha * max(0., 1. - d / self.radius) * col.alphaF())
                src.setPixel(x, y, col.rgba())

        r = self._radius
        center = pos2 - QPointF(r, r)

        p = QPainter(qimage)
        if clip_rect is not None:
            p.setClipRect(clip_rect)

        p.drawImage(center, src)

    def flood_fill(self, pos, qimage, clip_rect=None):
        orgpix = qimage.pixelColor(pos)
        orgpix = (orgpix.red(), orgpix.green(), orgpix.blue())
        todo = {(pos.x(), pos.y())}
        visited = set()

        def _check(p):
            if p in visited:
                return False
            c = qimage.pixelColor(p[0], p[1])
            d = (abs(orgpix[0] - c.red()) + abs(orgpix[1] - c.green()) + abs(orgpix[2] - c.blue())) / 3
            return d <= self.fill_tolerance

        while todo:
            pos = todo.pop()
            visited.add(pos)
            if pos[0] + 1 < qimage.width():
                if clip_rect is None or pos[0] + 1 <= clip_rect.right():
                    p = (pos[0]+1, pos[1])
                    if _check(p):
                        todo.add(p)
            if pos[1] + 1 < qimage.height():
                if clip_rect is None or pos[1] + 1 <= clip_rect.bottom():
                    p = (pos[0], pos[1]+1)
                    if _check(p):
                        todo.add(p)
            if pos[0] - 1 >= 0:
                if clip_rect is None or pos[0] - 1 >= clip_rect.left():
                    p = (pos[0]-1, pos[1])
                    if _check(p):
                        todo.add(p)
            if pos[1] - 1 >= 0:
                if clip_rect is None or pos[1] - 1 >= clip_rect.top():
                    p = (pos[0], pos[1]-1)
                    if _check(p):
                        todo.add(p)

        for p in visited:
            qimage.setPixel(p[0], p[1], self.color.rgba())

    @property
    def brush_image(self):
        if self._brush_qimage is None:
            self._brush_qimage = self._create_brush_qimage(self._color)
        return self._brush_qimage

    def _create_brush_qimage(self, color):
        image = QImage((self._radius-1)*2+1, (self._radius-1)*2+1, QImage.Format_RGBA8888)
        cx = image.width() / 2 - .5
        cy = image.height() / 2 - .5
        alpha = self.alpha / 255.
        for y in range(image.height()):
            for x in range(image.width()):
                dx, dy = cx-x, cy-y
                d = math.sqrt(dx*dx + dy*dy)
                col = QColor(color)
                col.setAlphaF(alpha * max(0., 1.- d / self.radius) * col.alphaF())
                image.setPixel(x, y, col.rgba())
        return image
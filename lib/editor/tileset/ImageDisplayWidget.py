from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .Brush import Brush


class ImageDisplayWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.setFixedSize(200, 200)

        self.image = None

        l = QVBoxLayout(self)
        self.setLayout(l)

        self.scroll_area = QScrollArea(self)
        l.addWidget(self.scroll_area)

        self.canvas = ImageDisplayCanvas(self)
        self.scroll_area.setWidget(self.canvas)

        self.zoom_bar = QScrollBar(Qt.Horizontal, self)
        l.addWidget(self.zoom_bar)
        self.zoom_bar.setRange(1, 50)
        self.zoom_bar.setValue(self.zoom)
        self.zoom_bar.valueChanged.connect(self.set_zoom)

    @property
    def zoom(self):
        return self.canvas.zoom

    def set_zoom(self, z):
        self.canvas.set_zoom(z)

    def set_image(self, img):
        self.image = img
        self.canvas.set_image(self.image)


class ImageDisplayCanvas(QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.image = None
        self._zoom = 3
        self.num_repeat = 4

    @property
    def zoom(self):
        return self._zoom

    def set_zoom(self, z):
        self._zoom = z
        self.setFixedSize(
            self.image.width() * self.zoom * self.num_repeat,
            self.image.height() * self.zoom * self.num_repeat)
        self.update()

    def set_image(self, img):
        self.image = img
        self.set_zoom(self.zoom)

    def paintEvent(self, e):
        if self.image is None:
            return
        p = QPainter(self)

        p.fillRect(
            0, 0,
            self.image.width() * self.num_repeat * self.zoom,
            self.image.height() * self.num_repeat * self.zoom,
            Qt.black)

        t = QTransform()
        t.scale(self.zoom, self.zoom)

        p.setTransform(t)

        for y in range(self.num_repeat):
            for x in range(self.num_repeat):
                p.drawImage(x*self.image.width(), y*self.image.height(), self.image)
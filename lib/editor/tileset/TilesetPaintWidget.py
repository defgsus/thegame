from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .TilesetPaintCanvas import TilesetPaintCanvas


class TilesetPaintWidget(QWidget):

    def __init__(self, tileset, brush, parent):
        super().__init__(parent)

        self.tileset = tileset
        self.brush = brush

        l = QVBoxLayout()
        self.setLayout(l)

        self.scroll_area = QScrollArea(self)
        l.addWidget(self.scroll_area)

        self.canvas = TilesetPaintCanvas(self.tileset, self.brush, self)
        self.scroll_area.setWidget(self.canvas)

        self.zoom_bar = QScrollBar(Qt.Horizontal, self)
        l.addWidget(self.zoom_bar)
        self.zoom_bar.setRange(1, 50)
        self.zoom_bar.setValue(self.canvas.zoom)
        self.zoom_bar.valueChanged.connect(self.set_zoom)

    def set_zoom(self, z):
        self.canvas.zoom = z


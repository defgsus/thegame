from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .TilesetPaintWidget import TilesetPaintWidget


class TilesetEditorWidget(QWidget):

    def __init__(self, tileset, parent):
        super().__init__(parent)

        self.tileset = tileset

        l = QHBoxLayout()
        self.setLayout(l)

        self.paint_widget = TilesetPaintWidget(self.tileset, self)
        l.addWidget(self.paint_widget)

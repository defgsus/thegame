from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .TilesetPaintWidget import TilesetPaintWidget
from .Brush import Brush


class TilesetEditorWidget(QWidget):

    def __init__(self, tileset, parent):
        super().__init__(parent)

        self.tileset = tileset
        self.brush = Brush()

        l = QHBoxLayout(self)
        self.setLayout(l)

        lv = QVBoxLayout()
        l.addLayout(lv)
        self._create_tool_widgets(lv)

        self.paint_widget = TilesetPaintWidget(self.tileset, self.brush, self)
        l.addWidget(self.paint_widget)

    def _create_tool_widgets(self, l):
        group = QButtonGroup(self)
        group.setExclusive(True)

        b = QPushButton("add", self)
        b.setCheckable(True)
        l.addWidget(b)
        group.addButton(b)
        b.setChecked(True)

        b = QPushButton("replace", self)
        b.setCheckable(True)
        l.addWidget(b)
        group.addButton(b)

        s = QSpinBox(self)
        l.addWidget(s)
        s.setRange(1, 100)
        s.setValue(self.brush.radius)
        s.setToolTip("brush radius")
        s.valueChanged.connect(self.brush.set_radius)

        b = QPushButton("fill", self)
        b.setCheckable(True)
        l.addWidget(b)
        group.addButton(b)

        l.addStretch(2)

from functools import partial

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .TilesetPaintWidget import TilesetPaintWidget
from .PaletteWidget import PaletteWidget
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

        lv = QVBoxLayout()
        l.addLayout(lv)

        self.paint_widget = TilesetPaintWidget(self.tileset, self.brush, self)
        self.paint_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lv.addWidget(self.paint_widget, 10)

        self.palette_widget = PaletteWidget(self)
        self.palette_widget.setMaximumHeight(180)
        #self.palette_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        lv.addWidget(self.palette_widget)
        self.palette_widget.colorChanged.connect(self.brush.set_color)

        self.brush.set_color(self.palette_widget.color)

    def _create_tool_widgets(self, l):
        group = QButtonGroup(self)
        group.setExclusive(True)

        for mode in sorted(Brush.MODES):
            b = QPushButton(mode, self)
            b.setCheckable(True)
            if self.brush.mode == mode:
                b.setChecked(True)
            b.clicked.connect(partial(self.brush.set_mode, mode))
            l.addWidget(b)
            group.addButton(b)

        s = QSpinBox(self)
        l.addWidget(s)
        s.setRange(1, 100)
        s.setValue(self.brush.radius)
        s.setToolTip("brush radius")
        s.valueChanged.connect(self.brush.set_radius)

        s = QSpinBox(self)
        l.addWidget(s)
        s.setRange(1, 255)
        s.setSingleStep(10)
        s.setValue(self.brush.alpha)
        s.setToolTip("brush alpha")
        s.valueChanged.connect(self.brush.set_alpha)

        b = QPushButton("fill", self)
        b.setCheckable(True)
        l.addWidget(b)
        group.addButton(b)

        l.addStretch(2)


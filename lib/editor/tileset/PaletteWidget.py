from functools import partial

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class PaletteWidget(QWidget):

    colorChanged = pyqtSignal(QColor)

    def __init__(self, parent):
        super().__init__(parent)

        self.color = QColor(255, 255, 255)
        self.selected_widget = None
        self.ignore_sbs = False

        lh = QHBoxLayout(self)
        self.setLayout(lh)

        lg = QGridLayout()
        lh.addLayout(lg)

        self.sbs = dict()
        for y, name in enumerate(("Red", "Green", "Blue", "Alpha")):
            sb = QSpinBox(self)
            sb.setToolTip(name)
            sb.setRange(0, 255)
            sb.setValue(255)
            sb.setSingleStep(10)
            sb.valueChanged.connect(self._value_changed)
            lg.addWidget(QLabel(name), y, 0)
            lg.addWidget(sb, y, 1)
            self.sbs[name] = sb

        lv = QVBoxLayout()
        lh.addLayout(lv)
        self.display = ColorDisplay(48, self)
        lv.addWidget(self.display)
        b = QPushButton(">", self)
        lv.addWidget(b)
        b.clicked.connect(self._to_palette)

        self.palette_widget = self._create_palette_widget()
        lh.addWidget(self.palette_widget)

        lh.addStretch(1)

        self.set_color(self.color)

    def set_color(self, c):
        self.color = c
        self.ignore_sbs = True
        self.sbs["Red"].setValue(c.red())
        self.sbs["Green"].setValue(c.green())
        self.sbs["Blue"].setValue(c.blue())
        self.sbs["Alpha"].setValue(c.alpha())
        self.ignore_sbs = False
        self._value_changed()

    @pyqtSlot(int)
    def _value_changed(self):
        if self.ignore_sbs:
            return
        self.color = QColor(
            self.sbs["Red"].value(),
            self.sbs["Green"].value(),
            self.sbs["Blue"].value(),
            self.sbs["Alpha"].value(),
        )
        self.display.set_color(self.color)
        self.colorChanged.emit(self.color)

    def _to_palette(self):
        if self.selected_widget is None:
            return
        self.selected_widget.color = self.color
        self.selected_widget.update()

    def _create_palette_widget(self):
        import random
        si = 16
        area = QScrollArea(self)
        area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        w = QWidget(area)
        w.setFixedSize(si*32, si*16)
        area.setWidget(w)
        lg = QGridLayout(w)
        lg.setContentsMargins(0, 0, 0, 0)
        lg.setSpacing(0)
        w.setLayout(lg)
        for y in range(16):
            for x in range(32):
                cw = ColorDisplay(si, w)
                cw.color = QColor(random.randrange(256), random.randrange(256), random.randrange(256))
                lg.addWidget(cw, y, x)
                cw.clicked.connect(self._palette_clicked)
        return area

    def _palette_clicked(self, w):
        if self.selected_widget is not None:
            self.selected_widget.is_selected = False
            self.selected_widget.update()
        w.is_selected = True
        w.update()
        self.selected_widget = w
        self.set_color(w.color)


class ColorDisplay(QWidget):

    clicked = pyqtSignal(QWidget)

    def __init__(self, size, parent):
        super().__init__(parent)
        self.setFixedSize(size, size)

        self.back_brush1 = QBrush(QColor(128,128,128))
        self.back_brush2 = QBrush(QColor(230,230,230))
        self.back_brush2.setStyle(Qt.Dense2Pattern)

        self.pen_normal = QPen(QColor(200,200,200))
        self.pen_selected = QPen(Qt.black)
        self.pen_selected.setWidth(3)

        self.color = QColor(255, 255, 255)
        self.is_selected = False

    def set_color(self, c):
        self.color = c
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        rect = self.rect().adjusted(1,1,-2,-2)
        p.setPen(Qt.NoPen)
        p.setBrush(self.back_brush1)
        p.drawRect(rect)
        p.setBrush(self.back_brush2)
        p.drawRect(rect)
        p.setBrush(QBrush(self.color))
        if self.is_selected:
            rect = self.rect().adjusted(0,0,-1,-1)
            p.setPen(self.pen_selected)
        else:
            p.setPen(self.pen_normal)
        p.drawRect(rect)

    def mousePressEvent(self, e):
        self.clicked.emit(self)

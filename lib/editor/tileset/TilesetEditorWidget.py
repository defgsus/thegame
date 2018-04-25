from functools import partial

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .TilesetPaintWidget import TilesetPaintWidget
from .PaletteWidget import PaletteWidget
from .ImageDisplayWidget import ImageDisplayWidget
from .Tileset import Tileset
from .Brush import Brush
from ..Files import Files


class TilesetEditorWidget(QWidget):

    hasChanged = pyqtSignal(bool)
    titleChanged = pyqtSignal(str)

    def __init__(self, tileset, parent):
        super().__init__(parent)

        self.tileset = tileset
        self.brush = Brush()
        self._is_changed = False

        lh = QHBoxLayout(self)
        self.setLayout(lh)

        lv = QVBoxLayout()
        lh.addLayout(lv)
        self._create_tool_widgets(lv)

        lv = QVBoxLayout()
        lh.addLayout(lv)

        self.paint_widget = TilesetPaintWidget(self.tileset, self.brush, self)
        self.paint_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lv.addWidget(self.paint_widget, 10)
        self.paint_widget.tilesetChanged.connect(self._on_tileset_change)
        self.paint_widget.selectedTileChanged.connect(self._on_selected_tileset_change)

        self.palette_widget = PaletteWidget(self)
        self.palette_widget.setMaximumHeight(180)
        #self.palette_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        lv.addWidget(self.palette_widget)
        self.palette_widget.colorChanged.connect(self.brush.set_color)

        self.brush.set_color(self.palette_widget.color)

        lv = QVBoxLayout()
        lh.addLayout(lv)

        self.tile_display = ImageDisplayWidget(self)
        lv.addWidget(self.tile_display)

        lv.addStretch(1)

    def _create_tool_widgets(self, l):
        group = QButtonGroup(self)
        group.setExclusive(True)

        b = QPushButton("select", self)
        b.setCheckable(True)
        b.clicked.connect(partial(self.brush.set_mode, "select"))
        l.addWidget(b)
        group.addButton(b)

        for mode in sorted(Brush.DRAW_MODES):
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
        b.clicked.connect(partial(self.brush.set_mode, "fill"))
        l.addWidget(b)
        group.addButton(b)

        s = QSpinBox(self)
        l.addWidget(s)
        s.setRange(0, 255)
        s.setValue(self.brush.fill_tolerance)
        s.setToolTip("fill tolerance")
        s.valueChanged.connect(self.brush.set_fill_tolerance)

        b = QPushButton("swipe", self)
        b.setCheckable(True)
        b.clicked.connect(partial(self.brush.set_mode, "swipe"))
        l.addWidget(b)
        group.addButton(b)

        l.addStretch(2)

    def create_menu(self, menu):
        menu.addAction("&Load tileset", self.slot_load_tileset, QKeySequence("Ctrl+O"))
        menu.addAction("&Save tileset as", self.slot_save_tileset, QKeySequence("Ctrl+Shift+S"))
        menu.addSeparator()
        menu.addAction("&Import image", self.slot_import_image)

    def set_changed(self, changed=True):
        do_emit = self._is_changed != changed
        self._is_changed = changed
        if do_emit:
            self.hasChanged.emit(self._is_changed)

    def set_tileset(self, tileset):
        self.tileset = tileset
        self.paint_widget.set_tileset(tileset)

    def _on_selected_tileset_change(self):
        img = self.paint_widget.canvas.get_tile_qimage()
        self.tile_display.set_image(img)

    def _on_tileset_change(self):
        self._on_selected_tileset_change()
        self.set_changed()

    def slot_load_tileset(self):
        filename = Files.get_open_filename(self, "tileset")
        if filename is None:
            return False
        try:
            tileset = Tileset(1, 1)
            tileset.load(filename)
        except BaseException as e:
            QMessageBox.critical(self, "Load error", "Unable to load tileset '%s'\n%s" % (filename, e))
            return False
        self.set_tileset(tileset)
        self.set_changed(True)
        shortname = filename.split("/")[-1]
        self.titleChanged.emit(shortname)
        return True

    def slot_save_tileset(self):
        filename = Files.get_save_filename(self, "tileset")
        if filename is None:
            return False
        self.tileset.save(filename)

        shortname = filename.split("/")[-1]
        self.titleChanged.emit(shortname)
        return True

    def slot_import_image(self):
        filename, __ = QFileDialog.getOpenFileName(
            self, self.tr("Import Tileset Image"), "", self.tr("Image files (*.*)"))
        if not filename:
            return False
        try:
            tileset = Tileset(self.tileset.tile_width, self.tileset.tile_height)
            tileset.load_image(filename)
        except BaseException as e:
            QMessageBox.critical(self, "Load error", "Unable to import tileset image '%s'\n%s" % (filename, e))
            return False
        self.set_tileset(tileset)
        self.set_changed(True)
        #shortname = filename.split("/")[-1]
        #self.titleChanged.emit(shortname)
        return True

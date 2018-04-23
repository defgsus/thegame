from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .ChunkEditorWidget import ChunkEditorWidget
from .EditedObjects import EditedObjects


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(self.tr("The Game Editor"))

        self.edited_objects = EditedObjects(self)

        self._create_main_menu()
        self._create_widgets()

        self.setGeometry(0, 0, 800, 600)

    def _create_main_menu(self):
        menu = self.menuBar().addMenu(self.tr("&File"))

        new_menu = menu.addMenu(self.tr("New"))

        menu.addAction(self.tr("&Open"), self.slot_open, QKeySequence("Ctrl+O"))
        menu.addAction(self.tr("E&xit"), self.slot_exit)

        new_menu.addAction(self.tr("&New Chunk"), self.slot_new_chunk, QKeySequence("Ctrl+N"))
        new_menu.addAction(self.tr("New &Tileset"), self.slot_new_tileset, QKeySequence("Ctrl+T"))

    def _create_widgets(self):
        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

    def slot_exit(self):
        self.close()

    def slot_open(self):
        filename = QFileDialog.getOpenFileName(
            self, self.tr("Open World"), "", self.tr("World Files (*.*)"))
        print(filename)

    def slot_new_chunk(self):
        self.create_tab("chunk")

    def slot_new_tileset(self):
        self.create_tab("tileset")

    def create_tab(self, what):
        if what == "chunk":
            obj = self.edited_objects.create_chunk()
            obj.tab = self.tab_widget.addTab(obj.widget, "new chunk")
        elif what == "tileset":
            obj = self.edited_objects.create_tileset()
            obj.tab = self.tab_widget.addTab(obj.widget, "new tileset")
        else:
            raise ValueError("Unknown tab '%s'" % what)
        return obj

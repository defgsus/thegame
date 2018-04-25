from functools import partial

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

        self.tab_menus = dict()
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

        for tab in sorted(self.edited_objects.object_types):
            m = self.menuBar().addMenu(self.edited_objects.object_types[tab][0])
            m.setEnabled(False)
            self.tab_menus[tab] = m

    def _create_widgets(self):
        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

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
        obj = self.edited_objects.create_object(what)
        obj.tab = self.tab_widget.addTab(obj.widget, obj.title)

        menu = self.tab_menus[obj.id_name]
        menu.clear()
        obj.create_menu(menu)
        obj.titleChanged.connect(partial(self.tab_widget.setTabText, obj.tab))
        return obj

    def _on_tab_changed(self):
        widget = self.tab_widget.currentWidget()
        obj = self.edited_objects.get_object_by_widget(widget)
        assert obj is not None

        menu = self.tab_menus[obj.id_name]
        menu.clear()
        obj.create_menu(menu)
        for tab in self.tab_menus:
            self.tab_menus[tab].setEnabled(tab == obj.id_name)
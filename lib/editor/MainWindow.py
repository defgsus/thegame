from PySide.QtCore import *
from PySide.QtGui import *

from .ChunkEditorWidget import ChunkEditorWidget


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(self.tr("The Game Editor"))

        self._create_main_menu()
        self._create_widgets()

        self.setGeometry(0, 0, 640, 480)

    def _create_main_menu(self):
        menu = self.menuBar().addMenu(self.tr("&File"))

        new_menu = menu.addMenu(self.tr("New"))

        menu.addAction(self.tr("&Open"), self.slot_open, QKeySequence("Ctrl+O"))
        menu.addAction(self.tr("E&xit"), self.slot_exit)

        new_menu.addAction(self.tr("&New Chunk"), self.slot_new_chunk, QKeySequence("Ctrl+N"))

    def _create_widgets(self):
        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

    @Slot()
    def slot_exit(self):
        self.close()

    @Slot()
    def slot_open(self):
        filename = QFileDialog.getOpenFileName(
            self, self.tr("Open World"), "", self.tr("World Files (*.*)"))
        print(filename)

    @Slot()
    def slot_new_chunk(self):
        self.create_tab("chunk")

    def create_tab(self, what):
        if what == "chunk":
            widget = ChunkEditorWidget(self)
            self.tab_widget.addTab(widget, "new chunk")
        else:
            raise ValueError("Unknown tab '%s'" % what)
        return widget

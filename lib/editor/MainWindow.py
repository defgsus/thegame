from PySide.QtCore import *
from PySide.QtGui import *


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self._create_main_menu()

        self.setGeometry(0, 0, 640, 480)

    def _create_main_menu(self):
        menu = self.menuBar().addMenu(self.tr("&File"))

        menu.addAction(self.tr("&Open"), self.slot_open, QKeySequence("Ctrl+O"))
        menu.addAction(self.tr("E&xit"), self.slot_exit)

    @Slot()
    def slot_exit(self):
        self.close()

    @Slot()
    def slot_open(self):
        filename = QFileDialog.getOpenFileName(
            self, self.tr("Open World"), "", self.tr("World Files (*.*)"))
        print(filename)



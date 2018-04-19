from PySide.QtCore import *
from PySide.QtGui import *

from .ChunkRenderWidget import ChunkRenderWidget


class ChunkEditorWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        l = QVBoxLayout()
        self.setLayout(l)

        self.render_widget = ChunkRenderWidget(self)
        l.addWidget(self.render_widget)

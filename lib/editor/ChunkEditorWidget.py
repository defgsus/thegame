from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .ToolsWidget import ToolsWidget
from .ChunkRenderWidget import ChunkRenderWidget


class ChunkEditorWidget(QWidget):

    def __init__(self, chunk, parent):
        super().__init__(parent)

        self.chunk = chunk

        l = QHBoxLayout()
        self.setLayout(l)

        self.render_widget = ChunkRenderWidget(self.chunk, self)
        l.addWidget(self.render_widget, 10)

        tools = (
            ("paint", "paint"),
            ("select", "select"),
        )
        self.tools_widget = ToolsWidget(tools, self)
        l.addWidget(self.tools_widget)

    def mouseMoveEvent(self, e):
        print(e.x(), e.y())

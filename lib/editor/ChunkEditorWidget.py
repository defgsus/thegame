from PySide.QtCore import *
from PySide.QtGui import *

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

        self.tools_widget = ToolsWidget(self)
        self.tools_widget.add_tool("paint", "paint")
        self.tools_widget.add_tool("select", "select")
        l.addWidget(self.tools_widget)

    def mouseMoveEvent(self, e):
        print(e.x(), e.y())

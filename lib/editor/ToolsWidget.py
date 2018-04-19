from PySide.QtCore import *
from PySide.QtGui import *

from .ChunkRenderWidget import ChunkRenderWidget


class ToolsWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.tools = dict()
        self.setLayout(QGridLayout())

    def add_tool(self, name, display):
        if name in self.tools:
            self.remove_tool(name)

        widget = QToolButton(self)
        widget.setText(display)
        widget.setAutoRaise(True)
        index = len(self.tools)
        self.layout().addWidget(widget, index, 0)
        self.tools[name] = {
            "index": index,
            "display": display,
            "widget": widget
        }

    def remove_tool(self, name):
        if name not in self.tools:
            return
        t = self.tools[name]
        self.layout().takeAt(t["index"], 0)
        t["widget"].deleteLater()
        del self.tools[name]

from functools import partial

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .ChunkRenderWidget import ChunkRenderWidget


class ToolsWidget(QWidget):

    def __init__(self, tools, parent):
        super().__init__(parent)
        l = QVBoxLayout()
        self.setLayout(l)

        self.tools = dict()
        for name, display in tools:
            widget = QToolButton(self)
            widget.setText(display)
            widget.setAutoRaise(True)
            widget.clicked.connect(partial(self.on_click, name))
            l.addWidget(widget)
            self.tools[name] = widget

        l.addStretch(10)

    def on_click(self, name):
        print(name)
        self.tools[name].setDown(True)

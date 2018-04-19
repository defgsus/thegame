import sys
from PySide import QtGui

from lib.editor import MainWindow

app = QtGui.QApplication(sys.argv)

win = MainWindow()
win.show()

sys.exit(app.exec_())

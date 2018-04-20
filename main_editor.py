import sys
from PyQt5.QtWidgets import *


from lib.editor import MainWindow

app = QApplication(sys.argv)

win = MainWindow()
win.show()

sys.exit(app.exec_())

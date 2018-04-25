import os

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Files:

    extensions = {
        "image": [bytes(f).decode("ascii") for f in QImageReader.supportedImageFormats()],
        "tileset": ["tgts"],
    }

    @staticmethod
    def get_open_filename(parent, type):
        assert type in Files.extensions
        extensions = " ".join("*.%s" % e for e in Files.extensions[type])

        filename, filter = QFileDialog.getOpenFileName(
            parent=parent,
            caption=parent.tr("Open %s") % type.capitalize(),
            directory="",
            filter=parent.tr("%s files (%s)") % (type, extensions),
        )
        if not filename:
            return None
        return filename

    @staticmethod
    def get_save_filename(parent, type):
        assert type in Files.extensions
        extensions = " ".join("*.%s" % e for e in Files.extensions[type])

        filename, filter = QFileDialog.getSaveFileName(
            parent=parent,
            caption=parent.tr("Save %s") % type.capitalize(),
            directory="",
            filter=parent.tr("%s files (%s)") % (type, extensions),
            options=QFileDialog.DontConfirmOverwrite,
        )
        if not filename:
            return None

        # complete filename
        endswith = False
        for ext in Files.extensions[type]:
            ext = ".%s" % ext
            if filename.endswith(ext):
                endswith = True
        if not endswith:
            filename += Files.extensions[type][0]

        # check for existence
        if os.path.exists(filename):
            res = QMessageBox.question(
                parent,
                parent.tr("File already exists"),
                parent.tr("The file %s already exists.\nDo you want to replace it?") % filename,
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.No
            )
            if res == QMessageBox.Cancel:
                return None

            if res == QMessageBox.No:
                return Files.get_save_filename(parent, type)

        return filename

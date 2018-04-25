from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from lib.world import *
from .ChunkEditorWidget import ChunkEditorWidget
from .tileset.TilesetEditorWidget import TilesetEditorWidget


class EditedObjects(QObject):

    def __init__(self, parent):
        super().__init__(parent)

        self.object_types = {
            "chunk": ("&Chunk", EditedChunk),
            "tileset": ("&Tileset", EditedTileset),
        }
        self.objects = {t: [] for t in self.object_types}

    def create_object(self, type):
        assert type in self.object_types
        Klass = self.object_types[type][1]
        obj = Klass(self.parent())
        obj.id_name = type
        self.objects[type].append(obj)
        return obj

    def get_object_by_widget(self, widget):
        for obj_list in self.objects.values():
            for obj in obj_list:
                if obj.widget == widget:
                    return obj
        return None


class EditedObject(QObject):

    hasChanged = pyqtSignal(bool)
    titleChanged = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        assert isinstance(parent, QWidget)
        self.parent_widget = parent
        self.title = "new"
        self.tab = None
        self.widget = None
        self.is_changed = False

    def create_menu(self, menu):
        if hasattr(self.widget, "create_menu"):
            self.widget.create_menu(menu)

    def set_widget(self, widget):
        self.widget = widget
        if hasattr(self.widget, "hasChanged"):
            self.widget.hasChanged.connect(self._on_change)
        if hasattr(self.widget, "titleChanged"):
            self.widget.titleChanged.connect(self.set_title)

    def set_title(self, title):
        self.title = title
        title = "%s%s" % ("*" if self.is_changed else "", self.title)
        self.titleChanged.emit(title)

    def _on_change(self, changed):
        self.is_changed = changed
        self.hasChanged.emit(changed)
        self.set_title(self.title)


class EditedChunk(EditedObject):

    def __init__(self, parent):
        super().__init__(parent)
        self.title = "new chunk"
        self.tileset = Tileset(16, 16)
        self.tileset.load("./assets/tileset02.png")
        self.chunk = WorldChunk(self.tileset)
        self.chunk.from_tiled("./assets/tiled/level01.json")
        self.set_widget(ChunkEditorWidget(self.chunk, self.parent_widget))


class EditedTileset(EditedObject):

    def __init__(self, parent):
        super().__init__(parent)
        from .tileset.Tileset import Tileset
        self.title = "new tileset"
        self.set_widget(TilesetEditorWidget(Tileset(16, 16, 16, 16), self.parent_widget))


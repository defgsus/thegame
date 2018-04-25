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


class EditedChunk:

    def __init__(self, parent):
        self.title = "new chunk"
        self.parent = parent
        self.tileset = Tileset(16, 16)
        self.tileset.load("./assets/tileset02.png")
        self.chunk = WorldChunk(self.tileset)
        self.chunk.from_tiled("./assets/tiled/level01.json")
        self.widget = ChunkEditorWidget(self.chunk, self.parent)
        self.tab = None

    def create_menu(self, menu):
        pass


class EditedTileset:

    def __init__(self, parent):
        from .tileset.Tileset import Tileset
        self.title = "new tileset"
        self.parent = parent
        self.tileset = Tileset(16, 16, 16, 16)
        #self.tileset.load("./assets/tileset02.png")
        self.widget = TilesetEditorWidget(self.tileset, self.parent)
        self.tab = None

    def create_menu(self, menu):
        return self.widget.create_menu(menu)

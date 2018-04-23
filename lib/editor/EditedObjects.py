from PyQt5.QtCore import *
from PyQt5.QtGui import *

from lib.world import *
from .ChunkEditorWidget import ChunkEditorWidget
from .tileset.TilesetEditorWidget import TilesetEditorWidget


class EditedObjects(QObject):

    def __init__(self, parent):
        super().__init__(parent)
        self.chunks = []
        self.tilesets = []

    def create_chunk(self):
        chunk = EditedChunk(self.parent())
        self.chunks.append(chunk)
        return chunk

    def create_tileset(self):
        obj = EditedTileset(self.parent())
        self.tilesets.append(obj)
        return obj


class EditedChunk:

    def __init__(self, parent):
        self.parent = parent
        self.tileset = Tileset(16, 16)
        self.tileset.load("./assets/tileset02.png")
        self.chunk = WorldChunk(self.tileset)
        self.chunk.from_tiled("./assets/tiled/level01.json")
        self.widget = ChunkEditorWidget(self.chunk, self.parent)
        self.tab = None


class EditedTileset:

    def __init__(self, parent):
        from .tileset.Tileset import Tileset
        self.parent = parent
        self.tileset = Tileset(16, 16)
        self.tileset.load("./assets/tileset02.png")
        self.widget = TilesetEditorWidget(self.tileset, self.parent)
        self.tab = None

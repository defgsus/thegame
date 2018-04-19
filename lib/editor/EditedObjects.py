from PySide.QtCore import *
from PySide.QtGui import *

from lib.world import *
from .ChunkEditorWidget import ChunkEditorWidget


class EditedObjects(QObject):

    def __init__(self, parent):
        super().__init__(parent)
        self.chunks = []

    def create_chunk(self):
        chunk = EditedChunk(self.parent())
        self.chunks.append(chunk)
        return chunk


class EditedChunk:

    def __init__(self, parent):
        self.parent = parent
        self.tileset = Tileset(16, 16)
        self.tileset.load("./assets/tileset02.png")
        self.chunk = WorldChunk(self.tileset)
        self.chunk.from_tiled("./assets/tiled/level01.json")
        self.widget = ChunkEditorWidget(self.chunk, self.parent)
        self.tab = None

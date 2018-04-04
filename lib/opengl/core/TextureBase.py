import ctypes
from .base import *


class TextureBase(OpenGlBaseObject):

    def __init__(self, target, name=None):
        super(TextureBase, self).__init__(name=name)
        self.target = target
        self.width = 0
        self.height = 0
        self.gpu_format = 0

    @staticmethod
    def set_active_texture(idx):
        glActiveTexture(GL_TEXTURE0 + idx)

    def _create(self):
        h = GLuint(0)
        glGenTextures(1, ctypes.byref(h))
        self._handle = h.value

    def _release(self):
        h = (GLuint * 1)(self._handle)
        glDeleteTextures(0, h)

    def _bind(self):
        glBindTexture(self.target, self._handle)

    def _unbind(self):
        glBindTexture(self.target, 0)

    def set_parameter(self, enum, value):
        glTexParameteri(self.target, enum, value)

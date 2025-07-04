from .base import *


class TextureBase(OpenGlBaseObject):

    GL_LINEAR = GL_LINEAR
    GL_NEAREST = GL_NEAREST
    GL_CLAMP = GL_CLAMP_TO_EDGE
    GL_REPEAT = GL_REPEAT

    def __init__(self, target, name=None):
        super(TextureBase, self).__init__(name=name)
        self.target = target
        self.width = 0
        self.height = 0
        self.gpu_format = 0
        self.mag_filter = self.GL_LINEAR
        self.min_filter = self.GL_NEAREST
        self.wrap_mode = self.GL_CLAMP
        self.multi_sample = 0

    @staticmethod
    def set_active_texture(idx: int):
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

    def set_parameter(self, enum, value=None):
        if self.multi_sample:
            return
        if value is None:
            if enum == GL_TEXTURE_MAG_FILTER:
                value = self.mag_filter
            elif enum == GL_TEXTURE_MIN_FILTER:
                value = self.min_filter
            else:
                raise ValueError("No value given/known for texture %s.setParameter(%s)" % (self.name, enum))
        glTexParameteri(self.target, enum, value)

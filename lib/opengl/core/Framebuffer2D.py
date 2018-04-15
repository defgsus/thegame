import ctypes
from .base import *


class Framebuffer2D(OpenGlBaseObject):
    def __init__(self, width, height, num_color_tex=1, with_depth_tex=True, name=None):
        from .Texture2D import Texture2D
        super(Framebuffer2D, self).__init__(name=name)
        self.width = width
        self.height = height
        self._rbo = -1
        self._color_textures = [Texture2D("%s-color-%s" % (self.name, i)) for i in range(num_color_tex)]
        self._depth_texture = Texture2D() if with_depth_tex else None
        self._color_texture_changed = set()

    def color_texture(self, index):
        if index >= len(self._color_textures):
            raise IndexError("color texture index %s out of range for %s" % (index, self))
        return self._color_textures[index]

    def depth_texture(self):
        return self._depth_texture

    def clear(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def swap_color_texture(self, index, tex):
        """
        Exchange current color texture with given texture.
        Changes take effect after bind()
        """
        ret = self._color_textures[index]
        if tex.width != ret.width or tex.height != ret.height:
            raise ValueError("Unmatched size (%s, %s) to FBO.swap_color_texture" % (tex.width, tex.height))
        self._color_textures[index] = tex
        self._color_texture_changed.add(index)
        return ret

    def _create(self):
        h = GLuint(0)
        glGenFramebuffers(1, ctypes.byref(h))
        self._handle = h.value

        if self._depth_texture is not None:
            glGenRenderbuffers(1, ctypes.byref(h))
            self._rbo = h.value

        self.bind()
        self._update_textures()

    def _release(self):
        if self._rbo >= 0:
            h = (GLuint * 1)(self._rbo)
            glDeleteRenderbuffers(1, h)
            self._rbo = -1
        h = (GLuint *1)(self._handle)
        glDeleteFramebuffers(1, h)

    def _bind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self._handle)
        self._update_textures()

    def _unbind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glBindRenderbuffer(GL_RENDERBUFFER, 0)

    def _update_textures(self):
        for i, tex in enumerate(self._color_textures):
            bind_tex = None
            # create attachment
            if not tex.is_created():
                tex.create()
                tex.bind()
                tex.upload(None, self.width, self.height, gpu_format=GL_RGBA32F)
                bind_tex = tex
            # resize attachment
            elif tex.width != self.width or tex.height != self.height:
                tex.bind()
                tex.upload(None, self.width, self.height, gpu_format=GL_RGBA32F)
                bind_tex = tex
            # swap attachment
            elif i in self._color_texture_changed:
                self._color_texture_changed.remove(i)
                bind_tex = tex

            if bind_tex:
                glBindFramebuffer(GL_FRAMEBUFFER, self._handle)
                glFramebufferTexture2D(
                    GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0 + i, GL_TEXTURE_2D, tex.handle, 0
                )

        if self._rbo >= 0:
            if self._depth_texture is not None:
                if not self._depth_texture.is_created():
                    self._depth_texture.create()
                    self._depth_texture.bind()
                    self._depth_texture.upload(None, self.width, self.height,
                                               input_format=GL_DEPTH_COMPONENT, gpu_format=GL_DEPTH_COMPONENT)
                    glBindRenderbuffer(GL_RENDERBUFFER, self._rbo)
                    glFramebufferTexture2D(
                        GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self._depth_texture.handle, 0
                    )


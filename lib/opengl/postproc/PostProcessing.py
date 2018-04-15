from ..core.Framebuffer2D import Framebuffer2D
from ..core.Texture2D import Texture2D


class PostProcessing:

    def __init__(self):
        self.fbo = Framebuffer2D(16, 16)
        self.stages = []

    def add_stage(self, proc):
        self.stages.append(proc)

    def release(self):
        for s in self.stages:
            s.release()

    def bind(self, width, height):
        if self.fbo.is_created():
            if self.fbo.width != width or self.fbo.height != height:
                self.fbo.release()
                self.fbo = Framebuffer2D(width, height)

        if not self.fbo.is_created():
            self.fbo.create()

        self.fbo.bind()
        self.fbo.clear()

    def draw(self, width, height, time):
        self.fbo.unbind()

        Texture2D.set_active_texture(0)
        self.fbo.color_texture(0).bind()

        if self.fbo.depth_texture():
            Texture2D.set_active_texture(1)
            self.fbo.depth_texture().bind()
            Texture2D.set_active_texture(0)

        for stage in self.stages:
            stage.draw(width, height, time)
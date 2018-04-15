from pyglet.gl import GL_RGBA32F

from ..core.Framebuffer2D import Framebuffer2D
from ..core.Texture2D import Texture2D


class PostProcessing:

    def __init__(self):
        self.fbo = Framebuffer2D(16, 16)
        self.fbo2 = None
        self.swap_tex = None
        self.stages = []

    def add_stage(self, proc):
        self.stages.append(proc)

    def release(self):
        for s in self.stages:
            s.release()
        if self.fbo.is_created():
            self.fbo.release()
        if self.fbo2.is_created():
            self.fbo2.release()
        if self.swap_tex and self.swap_tex.is_created():
            self.swap_tex.release()

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

        stages = []
        for stage in self.stages:
            for i in range(stage.num_stages):
                stages.append((stage, i))

        if not stages:
            raise ValueError("empty postprocessing")

        if len(stages) == 1:
            stages[0][0].draw(stages[0][1], width, height, time)
            return

        if self.fbo2 is None:
            self.fbo2 = Framebuffer2D(width, height)

        if self.fbo2.is_created():
            if self.fbo2.width != width or self.fbo2.height != height:
                self.fbo2.release()
                self.fbo2 = Framebuffer2D(width, height)

        if not self.fbo2.is_created():
            self.fbo2.create()

        self.fbo2.bind()
        self.fbo2.clear()

        for i, stage in enumerate(stages):
            last_frame = i+1 == len(stages)

            if last_frame:
                self.fbo2.unbind()

            stage[0].draw(stage[1], width, height, time)

            if self.swap_tex is None:
                self.swap_tex = Texture2D("pp-swap")
                self.swap_tex.create()
                self.swap_tex.bind()
                self.swap_tex.upload(None, width, height, gpu_format=GL_RGBA32F)
            self.swap_tex = self.fbo2.swap_color_texture(0, self.swap_tex)
            self.swap_tex.bind()

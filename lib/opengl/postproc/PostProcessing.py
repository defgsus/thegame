from pyglet.gl import *

from ..core.Framebuffer2D import Framebuffer2D
from ..core.Texture2D import Texture2D
from ..ScreenQuad import ScreenQuad


class PostProcessing:

    def __init__(self):
        self.num_color_tex = 2
        self.fbo = None
        self.fbo_down = None
        self.fbo2 = None
        self.swap_tex = None
        self.output_texture = [None] * (self.num_color_tex+1)
        self.stages = []
        self.output_quad = None
        self.multi_sample = 16

    def add_stage(self, proc):
        self.stages.append(proc)

    def release(self):
        for s in self.stages:
            s.release()
        if self.fbo.is_created():
            self.fbo.release()
        if self.fbo2.is_created():
            self.fbo2.release()
        if self.output_quad and self.output_quad.is_created():
            self.output_quad.release()
        if self.swap_tex and self.swap_tex.is_created():
            self.swap_tex.release()

    def bind(self, rs):
        #print("pp bind", rs.render_width, rs.render_height)
        if self.fbo is None:
            self.fbo = Framebuffer2D(rs.render_width, rs.render_height, name="render-fbo",
                                     num_color_tex=self.num_color_tex, multi_sample=self.multi_sample)
        if self.fbo.is_created():
            if self.fbo.width != rs.render_width or self.fbo.height != rs.render_height:
                self.fbo.release()
                self.fbo = Framebuffer2D(rs.render_width, rs.render_height, name="render-fbo",
                                         num_color_tex=self.num_color_tex, multi_sample=self.multi_sample)

        if not self.fbo.is_created():
            self.fbo.create()

        self.fbo.bind()
        glViewport(0, 0, rs.render_width, rs.render_height)
        self.fbo.clear()

        # keep rendered-to texture as current output
        for i in range(self.fbo.num_color_textures()):
            self.output_textures[i] = self.fbo.color_texture(i)
        self.output_textures = self.fbo.depth_texture()

    def render(self, rs):
        self.fbo.unbind()

        stages = []
        for stage in self.stages:
            for i in range(stage.num_stages):
                stages.append((stage, i))

        if self.multi_sample:
            self._downsample(rs)

        if not stages:
            return

        # bind postproc fbo
        if self.fbo2 is None:
            self.fbo2 = Framebuffer2D(rs.render_width, rs.render_height, with_depth_tex=None, name="pp-fbo")

        if self.fbo2.is_created():
            if self.fbo2.width != self.fbo.width or self.fbo2.height != self.fbo.height:
                self.fbo2.release()
                self.fbo2 = Framebuffer2D(self.fbo.width, self.fbo.height)

        if not self.fbo2.is_created():
            self.fbo2.create()

        self.fbo2.bind()
        self.fbo2.clear()
        glViewport(0, 0, self.fbo2.width, self.fbo2.height)

        # bind previous rendered outputs to tex1, tex2, ...
        for i in range(self.num_color_tex):
            Texture2D.set_active_texture(i)
            self.output_textures[i].bind()
            self.output_textures[i].set_parameter(GL_TEXTURE_MAG_FILTER)

        for i, stage in enumerate(stages):

            # bind previous output
            #print("in", i, self.output_texture)
            if i > 0:
                Texture2D.set_active_texture(0)
                self.output_textures[0].bind()

            # render pp stage
            self.fbo2.bind()
            self.fbo2.clear()
            stage[0].draw(stage[1], rs)

            # output of pp stage
            for i in range(self.fbo.num_color_textures()):
                self.output_textures[i] = self.fbo.color_texture(i)

            if len(stages) > 1:
                # swap stage output with swap_tex
                self._swap_tex()


        self.fbo2.unbind()
        #self.output_texture = self.swap_tex
        #print("out ", self.output_texture)
        
    def _downsample(self, rs):
        if self.fbo_down is None:
            self.fbo_down = Framebuffer2D(self.fbo.width, self.fbo.height, name="downsampler",
                                          num_color_tex=self.num_color_tex)
        if self.fbo_down.is_created():
            if self.fbo_down.width != self.fbo.width or self.fbo_down.height != self.fbo.height:
                self.fbo_down.release()
                self.fbo_down = Framebuffer2D(self.fbo.width, self.fbo.height, name="downsampler",
                                              num_color_tex=self.num_color_tex)
        if not self.fbo_down.is_created():
            self.fbo_down.create()

        glBindFramebuffer(GL_READ_FRAMEBUFFER, self.fbo.handle)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self.fbo_down.handle)
        for i in range(self.fbo.num_color_textures()):
            glReadBuffer(GL_COLOR_ATTACHMENT0+i)
            glDrawBuffer(GL_COLOR_ATTACHMENT0+i)
            glBlitFramebuffer(0, 0, self.fbo.width, self.fbo.height,
                              0, 0, self.fbo.width, self.fbo.height,
                              GL_COLOR_BUFFER_BIT, GL_NEAREST)
            self.output_textures[i] = self.fbo_down.color_texture(i)
        glBindFramebuffer(GL_READ_FRAMEBUFFER, 0)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
        glReadBuffer(GL_COLOR_ATTACHMENT0)
        glDrawBuffer(GL_COLOR_ATTACHMENT0)

    def _swap_tex(self):
        if self.swap_tex is None:
            self.swap_tex = Texture2D(name="pp-swap")
            self.swap_tex.create()
            self.swap_tex.bind()
            self.swap_tex.upload(None, self.fbo.width, self.fbo.height, gpu_format=GL_RGBA32F)
        self.swap_tex = self.fbo2.swap_color_texture(0, self.swap_tex)

    def render_output(self, rs):
        self.fbo.unbind()

        if self.output_quad is None:
            self.output_quad = ScreenQuad()

        glViewport(0, 0, rs.screen_width, rs.screen_height)

        Texture2D.set_active_texture(0)
        self.output_textures[0].bind()
        self.output_textures[0].set_parameter(GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        self.output_quad.draw_centered(
            rs.screen_width, rs.screen_height,
            rs.render_width, rs.render_height
        )

from pyglet.gl import *

from ..core.Framebuffer2D import Framebuffer2D
from ..core.Texture2D import Texture2D
from ..ScreenQuad import ScreenQuad


class PostProcessing:

    def __init__(self):
        self.fbo = None
        self.fbo2 = None
        self.swap_tex = None
        self.stages = []
        self.output_texture = None
        self.output_quad = None

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
            self.fbo = Framebuffer2D(rs.render_width, rs.render_height, name="render-fbo")
        if self.fbo.is_created():
            if self.fbo.width != rs.render_width or self.fbo.height != rs.render_height:
                self.fbo.release()
                self.fbo = Framebuffer2D(rs.render_width, rs.render_height, name="render-fbo")

        if not self.fbo.is_created():
            self.fbo.create()

        self.fbo.bind()
        glViewport(0, 0, rs.render_width, rs.render_height)
        self.fbo.clear()
        self.output_texture = self.fbo.color_texture(0)

    def render(self, rs):
        self.fbo.unbind()

        stages = []
        for stage in self.stages:
            for i in range(stage.num_stages):
                stages.append((stage, i))

        if not stages:
            #raise ValueError("empty postprocessing")
            return

        # bind postproc fbo
        if self.fbo2 is None:
            self.fbo2 = Framebuffer2D(rs.render_width, rs.render_height, with_depth_tex=False, name="pp-fbo")

        if self.fbo2.is_created():
            if self.fbo2.width != self.fbo.width or self.fbo2.height != self.fbo.height:
                self.fbo2.release()
                self.fbo2 = Framebuffer2D(self.fbo.width, self.fbo.height)

        if not self.fbo2.is_created():
            self.fbo2.create()

        self.fbo2.bind()
        self.fbo2.clear()
        glViewport(0, 0, self.fbo2.width, self.fbo2.height)

        # bind previous rendered output to tex1
        Texture2D.set_active_texture(0)
        self.output_texture.bind()
        self.output_texture.set_parameter(GL_TEXTURE_MAG_FILTER)

        # bind previous rendered depth output to tex2
        if self.fbo.depth_texture():
            Texture2D.set_active_texture(1)
            self.fbo.depth_texture().bind()
            Texture2D.set_active_texture(0)

        #self.swap_tex = self.fbo2.color_texture(0)
        for i, stage in enumerate(stages):

            # bind previous output
            #print("in", i, self.output_texture)
            Texture2D.set_active_texture(0)
            self.output_texture.bind()

            # render pp stage
            self.fbo2.bind()
            stage[0].draw(stage[1], rs)

            # output of pp stage
            self.output_texture = self.fbo2.color_texture(0)

            if len(stages) > 1:
                # swap stage output with swap_tex
                if self.swap_tex is None:
                    self.swap_tex = Texture2D("pp-swap")
                    self.swap_tex.create()
                    self.swap_tex.bind()
                    self.swap_tex.upload(None, self.fbo.width, self.fbo.height, gpu_format=GL_RGBA32F)
                self.swap_tex = self.fbo2.swap_color_texture(0, self.swap_tex)


        self.fbo2.unbind()
        #self.output_texture = self.swap_tex
        #print("out ", self.output_texture)

    def render_output(self, rs):
        self.fbo.unbind()

        if self.output_quad is None:
            self.output_quad = ScreenQuad()

        glViewport(0, 0, rs.screen_width, rs.screen_height)

        Texture2D.set_active_texture(0)
        self.output_texture.bind()
        self.output_texture.set_parameter(GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        self.output_quad.draw_centered(
            rs.screen_width, rs.screen_height,
            rs.render_width, rs.render_height
        )

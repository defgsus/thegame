from .core.base import *
from .core.Framebuffer2D import Framebuffer2D
from .core.Texture2D import Texture2D
from .ScreenQuad import ScreenQuad
from .RenderGraph import RenderGraph
from ..graph.DirectedGraph import DirectedGraph


class RenderPipeline:

    def __init__(self, graph):
        self.graph = graph
        self.render_settings = None
        # get serial list of RenderStages
        node_names = self.graph.graph.serialize()
        self.stages = [RenderStage(self, self.graph.to_node(n)) for n in node_names]
        self._stage_dict = {s.node.name: s for s in self.stages}
        self._quad = None

    def get_stage(self, name):
        return self._stage_dict.get(name)

    def render(self, rs):
        self.render_settings = rs
        for stage in self.stages:
            stage.render()

    def render_to_screen(self, rs):
        """Render final stage to screen"""
        assert len(self.stages)
        if not self._quad:
            self._quad = ScreenQuad()
        tex = self.stages[-1].get_output_texture(0)
        Texture2D.set_active_texture(0)
        tex.bind()
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, rs.screen_width, rs.screen_height)
        self._quad.draw_centered(rs.screen_width, rs.screen_height,
                                 rs.render_width, rs.render_height)

    def dump(self):
        for stage in self.stages:
            print(stage)


class RenderStage:
    """Internal class to handle a RenderNode and it's FBOs"""

    def __init__(self, pipeline, node):
        self.pipeline = pipeline
        self.node = node
        self.fbo = None
        self.fbo_down = None

        self.inputs = []
        if self.node.name in self.graph.inputs:
            ins = self.graph.inputs[self.node.name]
            for in_slot in ins:
                self.inputs.append({
                    "from_node": ins[in_slot][0],
                    "from_slot": ins[in_slot][1],
                    "to_slot": in_slot,
                })
        self.inputs.sort(key=lambda i: i["to_slot"])

    def __str__(self):
        inf = "%s" % self.node
        outs = self.node.output_slots()
        if outs:
            inf += ", outs=[%s]" % ", ".join("%s" % o for o in outs)
        if self.inputs:
            inf += ", ins=[%s]" % ", ".join(
                "%(to_slot)s: %(from_node)s:%(from_slot)s" % i for i in self.inputs)
        inf += ")"
        return "Stage(%s)" % inf

    @property
    def graph(self):
        return self.pipeline.graph

    @property
    def width(self):
        return self.pipeline.render_settings.render_width

    @property
    def height(self):
        return self.pipeline.render_settings.render_height

    def render(self):
        # create node assets or whatever
        if not self.node.is_created:
            self.node.create(self.pipeline.render_settings)
            self.node.is_created = True

        # build and bind this stage's FBO
        self._update_fbo()
        self.fbo.bind()
        self.fbo.set_viewport()
        self.fbo.clear()

        # bind input textures
        for input in self.inputs:
            stage = self.pipeline.get_stage(input["from_node"])
            tex = stage.get_output_texture(input["from_slot"])
            Texture2D.set_active_texture(input["to_slot"])
            tex.bind()

        self.node.render(self.pipeline.render_settings)
        self.fbo.unbind()

        if self.node.num_multi_sample():
            self._downsample()

    def get_output_texture(self, slot):
        fbo = self.fbo if not self.node.num_multi_sample() else self.fbo_down
        if not fbo:
            raise ValueError("FBO not yet initialized in node '%s'" % self.node.name)
        if isinstance(slot, int):
            if slot >= self.node.num_color_outputs():
                raise ValueError("Request for output slot %s ot of range for node '%s'" % (slot, self.node.name))
            return fbo.color_texture(slot)
        elif slot == "depth":
            if fbo.has_depth_texture():
                return fbo.depth_texture()
            raise ValueError("Node '%s' has no depth output" % self.node.name)
        raise ValueError("Node '%s' has no output slot '%s'" % (self.node.name, slot))

    def _update_fbo(self):
        if self.fbo is None:
            self.fbo = self._create_fbo()
        if self.fbo.is_created():
            if self.fbo.width != self.width or self.fbo.height != self.height:
                self.fbo.release()
                self.fbo = self._create_fbo()
        else:
            self.fbo.create()

        if self.fbo_down is None:
            self.fbo_down = self._create_downsample_fbo()
        if self.fbo_down.is_created():
            if self.fbo_down.width != self.width or self.fbo_down.height != self.height:
                self.fbo_down.release()
                self.fbo_down = self._create_downsample_fbo()
        if not self.fbo_down.is_created():
            self.fbo_down.create()

    def _create_fbo(self):
        return Framebuffer2D(
            self.width, self.height, name=self.node.name,
            num_color_tex=self.node.num_color_outputs(),
            with_depth_tex=self.node.has_depth_output(),
            multi_sample=self.node.num_multi_sample()
        )

    def _create_downsample_fbo(self):
        return Framebuffer2D(
            self.width, self.height, name="%s-down" % self.node.name,
            num_color_tex=self.node.num_color_outputs(),
            with_depth_tex=self.node.has_depth_output()
        )

    def _downsample(self):
        glBindFramebuffer(GL_READ_FRAMEBUFFER, self.fbo.handle)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self.fbo_down.handle)
        for i in range(self.fbo.num_color_textures()):
            glReadBuffer(GL_COLOR_ATTACHMENT0+i)
            glDrawBuffer(GL_COLOR_ATTACHMENT0+i)
            bits = GL_COLOR_BUFFER_BIT
            if i == 0:
                bits |= GL_DEPTH_BUFFER_BIT
            glBlitFramebuffer(0, 0, self.fbo.width, self.fbo.height,
                              0, 0, self.fbo.width, self.fbo.height,
                              bits, GL_NEAREST)
        glBindFramebuffer(GL_READ_FRAMEBUFFER, 0)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
        glReadBuffer(GL_COLOR_ATTACHMENT0)
        glDrawBuffer(GL_COLOR_ATTACHMENT0)

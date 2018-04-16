from .core.base import *
from .core.Framebuffer2D import Framebuffer2D
from .core.Texture2D import Texture2D
from .RenderGraph import RenderGraph


class RenderPipeline:

    def __init__(self, graph):
        self.graph = graph
        self.render_settings = None
        self.stages = []
        self._linearize()
        self._stage_dict = {s.node.name: s for s in self.stages}

    def get_stage(self, name):
        return self._stage_dict.get(name)

    def render(self, rs):
        self.render_settings = rs
        for stage in self.stages:
            stage.render()

    def _linearize(self):
        # build helper struct
        graph = DirectedGraphHelper()
        for n1 in self.graph.edges:
            for n2 in self.graph.edges[n1]:
                graph.add_edge(n1, n2)

        # nodes with no inputs (temporary space)
        beginnings = set()

        # collect them
        for n in self.graph.nodes:
            if graph.has_inputs(n):
                beginnings.add(n)

        if not beginnings:
            raise ValueError("No start nodes in RenderGraph")

        # grab a node from start list
        while beginnings:
            n = beginnings.pop()

            # for each outgoing edge
            for nout in self.graph.node_outputs(n):

                # put to list
                self.stages.append(
                    RenderStage(self, self.graph.to_node(nout))
                )

                # remove this edge
                graph.remove_edge(n, nout)

                # if no other input node, move to beginnings

                if not graph.has_inputs(nout):
                    beginnings.add(nout)

        for n in graph.edges:
            if graph.has_inputs(n):
                raise ValueError("Loop in RenderGraph involving node '%s'" % n)


class DirectedGraphHelper:
    def __init__(self):
        self.nodes = set()
        self.edges = dict()
        self.inputs = dict()

    def add_edge(self, n1, n2):
        self.nodes.add(n1)
        self.nodes.add(n2)
        if n1 not in self.edges:
            self.edges[n1] = {n2}
        else:
            self.edges[n1].add(n2)
        if n2 not in self.inputs:
            self.inputs[n2] = {n1}
        else:
            self.inputs[n2].add(n1)

    def remove_edge(self, n1, n2):
        if n1 in self.edges:
            if n2 in self.edges[n1]:
                self.edges[n1].remove(n2)
        if n2 in self.inputs:
            if n1 in self.inputs[n2]:
                self.inputs[n2].remove(n1)

    def has_inputs(self, n):
        return n in self.inputs and self.inputs[n]


class RenderStage:

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
        # build and bind this stage's FBO
        self._update_fbo()
        self.fbo.bind()
        self.fbo.set_viewport()
        self.fbo.clear()

        # bind input textures
        for input in self.inputs:
            stage = self.graph.get_stage(input["from_node"])
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
            if slot >= self.node.num_color_textures():
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
            num_color_tex=self.node.num_color_textures(),
            with_depth_tex=self.node.has_depth_output(),
            multi_sample=self.node.num_multi_sample()
        )

    def _create_downsample_fbo(self):
        return Framebuffer2D(
            self.width, self.height, name="%s-down" % self.node.name,
            num_color_tex=self.node.num_color_textures(),
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

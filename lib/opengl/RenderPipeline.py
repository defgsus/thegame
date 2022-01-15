from typing import Union, Optional, Dict

from .core.base import *
from .core.Framebuffer2D import Framebuffer2D
from .core.Texture2D import Texture2D
from .ScreenQuad import ScreenQuad
from .RenderGraph import RenderGraph
from .RenderSettings import RenderSettings
from .RenderNode import RenderNode
from tests.util import Timer


class RenderPipeline:

    def __init__(self, graph: RenderGraph):
        self.graph = graph
        self.render_settings = None
        # get serial list of RenderStages
        node_names = self.graph.graph.serialize()
        self.stages = [RenderStage(self, self.graph.to_node(n)) for n in node_names]
        self._stage_dict = {s.node.name: s for s in self.stages}
        self._quad = None
        self.verbose = 0
        self._stage_times = dict()

    def get_stage(self, name: str) -> Optional["RenderStage"]:
        return self._stage_dict.get(name)

    def render(self, rs: RenderSettings):
        self.debug(1, "render %s" % rs)
        self.render_settings = rs
        for stage in self.stages:
            with Timer() as timer:
                timings = stage.render()
            self._stage_times[stage.node.name] = (timer, timings)

        for name, (timer, timers) in self._stage_times.items():
            if timer.fps() < 60.:
                print("TOO SLOW:", name, timer, timers)

    def render_to_screen(self, rs: RenderSettings):
        self.debug(1, "render_to_screen %s" % rs)
        """Render final stage to screen"""
        assert len(self.stages)
        if not self._quad:
            self._quad = ScreenQuad()

        tex = self.stages[-1].get_output_texture(0)
        Texture2D.set_active_texture(0)
        tex.bind()
        if rs.mag_filter is not None:
            tex.set_parameter(GL_TEXTURE_MAG_FILTER, rs.mag_filter)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, rs.screen_width, rs.screen_height)
        self._quad.draw_centered(rs.screen_width, rs.screen_height,
                                 rs.render_width, rs.render_height)

    def debug(self, level: int, text):
        if self.verbose >= level:
            print("Pipeline: %s" % text)

    def dump(self):
        print("[%s]" % "->".join(s.node.name for s in self.stages))
        for stage in self.stages:
            if not stage.inputs:
                self._dump_stage(stage)

    def _dump_stage(self, stage, indent=""):
        print("%s%s" % (indent, stage))
        outs = self.graph.output_nodes(stage.node.name)
        for o in outs:
            self._dump_stage(self._stage_dict[o], indent + "  ")

    def benchmark(self, rs: Optional[RenderSettings] = None, max_sec: float = 3.):
        import time
        start_time = time.time()
        cur_time = 0
        num_frame = 0
        while cur_time < max_sec:
            self.render(rs or self.render_settings)
            glFlush()
            glFinish()
            cur_time = time.time() - start_time
            num_frame += 1
        fps = num_frame / cur_time
        print("rendered %s frames in %s seconds (%s fps)" % (num_frame, round(cur_time, 2), round(fps, 1)))
        return fps


class RenderStage:
    """Internal class to handle a RenderNode and it's FBOs"""

    def __init__(self, pipeline: RenderPipeline, node: RenderNode):
        self.pipeline = pipeline
        self.node = node
        self.fbo = None
        self.fbo_down = None
        self.swap_texture = None

        self.inputs = []
        if self.node.name in self.graph.inputs:
            self.inputs = list(self.graph.inputs[self.node.name].values())
        self.inputs.sort(key=lambda i: i["to_slot"])

    def __repr__(self):
        return self.__str__()

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

    def debug(self, level: int, text):
        self.pipeline.debug(level, "Stage('%s'): %s" % (self.node.name, text))

    @property
    def graph(self) -> RenderGraph:
        return self.pipeline.graph

    @property
    def width(self) -> int:
        return self.pipeline.render_settings.render_width

    @property
    def height(self) -> int:
        return self.pipeline.render_settings.render_height

    def render(self) -> Dict[str, float]:
        from .TextureNode import Texture2DNode
        timings = {}

        self.debug(2, "render")
        # create node assets or whatever
        if not self.node.is_created:
            with Timer() as timer:
                self.debug(3, "create node")
                self.node.create(self.pipeline.render_settings)
                self.node.is_created = True
            timings["node_create"] = timer

        if isinstance(self.node, Texture2DNode):
            return timings

        with Timer() as timer:
            # build and bind this stage's FBO
            self._update_fbo()
            self.debug(4, "bind fbo %s" % self.fbo)
            self.fbo.bind()
            self.fbo.set_viewport()
            self.fbo.clear()
        timings["bind_fbo"] = timer

        # bind input textures
        with Timer() as timer:
            for input in self.inputs:
                stage = self.pipeline.get_stage(input["from_node"])
                tex = stage.get_output_texture(input["from_slot"])
                Texture2D.set_active_texture(input["to_slot"])
                self.debug(4, "bind tex %s to %s" % (input["to_slot"], tex))
                tex.bind()
                if input["mag_filter"] is not None:
                    tex.set_parameter(GL_TEXTURE_MAG_FILTER, input["mag_filter"])
                if input["min_filter"] is not None:
                    tex.set_parameter(GL_TEXTURE_MIN_FILTER, input["min_filter"])
        timings["bind_textures"] = timer

        if self.node.num_passes() < 2:
            try:
                self.debug(3, "render node %s" % self.node)
                with Timer() as timer:
                    self.node.render(self.pipeline.render_settings, 0)
                    self.fbo.unbind()
                timings["render"] = timer
            except BaseException as e:
                raise e.__class__(f"in RenderNode {self.node.name}: {e.__class__.__name__}: {e}")
        else:
            for pass_num in range(self.node.num_passes()):
                self.debug(4, f"pass #{pass_num}")

                if pass_num > 0:
                    self.debug(4, f"bind tex 0 to {self.swap_texture}")
                    Texture2D.set_active_texture(0)
                    self.swap_texture.bind()

                glDisable(GL_DEPTH_TEST)
                self.debug(3, f"render node {self.node}")
                self.node.render(self.pipeline.render_settings, pass_num)

                if pass_num + 1 < self.node.num_passes():
                    self._swap_texture()
                    self.fbo.bind()

            self.fbo.unbind()

        if self.node.num_multi_sample():
            with Timer() as timer:
                self._downsample()
            timings["downsample"] = timer

        return timings

    def get_output_texture(self, slot: Union[int, str]) -> Texture2D:
        from .TextureNode import Texture2DNode

        if isinstance(slot, int):
            if slot >= self.node.num_color_outputs():
                raise ValueError("Request for output slot %s ot of range for node '%s'" % (slot, self.node.name))

        if isinstance(self.node, Texture2DNode):
            return self.node.texture

        fbo = self.fbo if not self.node.num_multi_sample() else self.fbo_down
        if not fbo:
            raise ValueError("FBO not yet initialized in node '%s'" % self.node.name)
        if isinstance(slot, int):
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

        if not self.fbo.is_created():
            self.fbo.create()

        if self.node.num_multi_sample() > 0:
            if self.fbo_down is None:
                self.fbo_down = self._create_downsample_fbo()
            if self.fbo_down.is_created():
                if self.fbo_down.width != self.width or self.fbo_down.height != self.height:
                    self.fbo_down.release()
                    self.fbo_down = self._create_downsample_fbo()
            if not self.fbo_down.is_created():
                self.fbo_down.create()

    def _create_fbo(self):
        fbo = Framebuffer2D(
            self.width, self.height, name="%s-fbo" % self.node.name,
            num_color_tex=self.node.num_color_outputs(),
            with_depth_tex=self.node.has_depth_output(),
            multi_sample=self.node.num_multi_sample()
        )
        self.debug(2, "created fbo %s" % fbo)
        return fbo

    def _create_downsample_fbo(self):
        fbo = Framebuffer2D(
            self.width, self.height, name="%s-downfbo" % self.node.name,
            num_color_tex=self.node.num_color_outputs(),
            with_depth_tex=self.node.has_depth_output()
        )
        self.debug(2, "created down-fbo %s" % fbo)
        return fbo

    def _downsample(self):
        self.debug(3, "downsampling")
        glBindFramebuffer(GL_READ_FRAMEBUFFER, self.fbo.handle)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self.fbo_down.handle)
        for i in range(self.fbo.num_color_textures()):
            glReadBuffer(GL_COLOR_ATTACHMENT0 + i)
            glDrawBuffer(GL_COLOR_ATTACHMENT0 + i)
            bits = GL_COLOR_BUFFER_BIT
            if i == 0:
                bits |= GL_DEPTH_BUFFER_BIT
            glBlitFramebuffer(0, 0, self.fbo.width, self.fbo.height,
                              0, 0, self.fbo.width, self.fbo.height,
                              bits, GL_NEAREST)
        glReadBuffer(GL_COLOR_ATTACHMENT0)
        glDrawBuffer(GL_COLOR_ATTACHMENT0)
        glBindFramebuffer(GL_READ_FRAMEBUFFER, 0)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)

    def _swap_texture(self):
        if not self.swap_texture:
            self.swap_texture = Texture2D(name="%s-fbo-swap" % self.node.name)

        if self.swap_texture.width != self.fbo.width and self.swap_texture.height != self.fbo.height:
            if not self.swap_texture.is_created():
                self.swap_texture.create()
            self.swap_texture.bind()
            self.swap_texture.upload(None, self.fbo.width, self.fbo.height, gpu_format=GL_RGBA32F)
            self.debug(2, "updated swap texture %s" % self.swap_texture)

        self.swap_texture = self.fbo.swap_color_texture(0, self.swap_texture)
        self.debug(3, "swapped fbo texture %s" % self.swap_texture)

from ..RenderNode import RenderNode
from ..ScreenQuad import ScreenQuad


class PostProcNode(RenderNode):

    def __init__(self, name):
        super().__init__(name)

        self.quad = ScreenQuad()
        self.do_compile = True
        self.num_stages = 1

    def release(self):
        self.quad.release()

    def render(self, rs):
        if self.do_compile:
            self.quad.set_shader_code(self.get_code())
            self.do_compile = False
        self.quad.drawable.shader.set_uniform("u_tex1", 0)
        self.quad.drawable.shader.set_uniform("u_tex2", 1)
        self.quad.drawable.shader.set_uniform("u_tex3", 2)
        self.quad.drawable.shader.set_uniform("u_tex4", 3)
        self.quad.drawable.shader.set_uniform("u_time", rs.time)
        self.update_uniforms(self.quad.drawable.shader, rs)
        self.quad.draw(rs.render_width, rs.render_height)
        #self.quad.draw_centered(rs.render_width, rs.render_height, rs.render_width, rs.render_height)

    def get_code(self):
        raise NotImplemented

    def update_uniforms(self, shader, rs):
        pass

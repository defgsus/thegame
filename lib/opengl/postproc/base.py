from ..ScreenQuad import ScreenQuad


class PostProcBase:

    def __init__(self):
        self.quad = ScreenQuad()
        self.width = 0
        self.height = 0
        self.do_compile = True
        self.num_stages = 1

    def get_code(self):
        raise NotImplemented

    def release(self):
        self.quad.release()

    def update_uniforms(self, shader, stage_num):
        pass

    def draw(self, stage_num, width, height, time):
        if self.do_compile:
            self.quad.set_shader_code(self.get_code())
            self.do_compile = False
        self.width = width
        self.height = height
        self.quad.drawable.shader.set_uniform("u_tex1", 0)
        self.quad.drawable.shader.set_uniform("u_tex2", 1)
        self.quad.drawable.shader.set_uniform("u_time", time)
        self.update_uniforms(self.quad.drawable.shader, stage_num)
        self.quad.draw(width, height)



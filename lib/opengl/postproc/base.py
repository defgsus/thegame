from ..ScreenQuad import ScreenQuad


class PostProcBase:

    def __init__(self):
        self.quad = ScreenQuad()
        self.quad.set_shader_code(self.get_code())

    def get_code(self):
        raise NotImplemented

    def release(self):
        self.quad.release()

    def draw(self, width, height, time):
        self.quad.drawable.shader.set_uniform("u_tex1", 0)
        self.quad.drawable.shader.set_uniform("u_tex2", 1)
        self.quad.drawable.shader.set_uniform("u_time", time)
        self.quad.draw(width, height)



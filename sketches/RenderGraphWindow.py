import time

import pyglet
import glm

from lib.opengl import *
from lib.world import *
from lib.geom import *


class ColorNode(RenderNode):

    def __init__(self, name):
        super().__init__(name)
        self.quad = ScreenQuad()
        self.quad.set_shader_code("""
        #line 15
        void mainImage(out vec4 fragColor, in vec2 fragCoord, in vec2 texCoord) {
            //fragColor = texture(u_tex1, texCoord);
            vec3 col = .5 + .5 * sin(texCoord.xyx * vec3(1,1,1.3) * 2 + u_time * vec3(3,5,7)/5.);
            fragColor = vec4(col, 1);
        }
        """)

    def release(self):
        self.quad.release()

    def render(self, rs):
        self.quad.drawable.shader.set_uniform("u_time", rs.time)
        self.quad.draw(rs.render_width, rs.render_height)


class GridNode(RenderNode):

    def __init__(self, name):
        super().__init__(name)
        self.quad = ScreenQuad()
        self.quad.set_shader_code("""
        #line 37
        void mainImage(out vec4 fragColor, in vec2 fragCoord, in vec2 texCoord) {
            vec2 mp = mod(texCoord * 10., 1.);
            float grid = max(smoothstep(.1,.0,abs(mp.x-.5)), smoothstep(.1,.0,abs(mp.y-.5)));
            fragColor = vec4(vec3(grid), 1);
        }
        """)

    def release(self):
        self.quad.release()

    def render(self, rs):
        self.quad.drawable.shader.set_uniform("u_time", rs.time)
        self.quad.draw(rs.render_width, rs.render_height)


class CombineNode(RenderNode):

    def __init__(self, name, operator):
        super().__init__(name)
        self.operator = operator
        self.quad = ScreenQuad()
        self.quad.set_shader_code("""
        #line 60
        void mainImage(out vec4 fragColor, in vec2 fragCoord, in vec2 texCoord) {
            vec4 c1 = texture(u_tex1, texCoord);
            vec4 c2 = texture(u_tex2, texCoord);
            fragColor = c1 %s c2;
        }
        """ % self.operator)

    def release(self):
        self.quad.release()

    def render(self, rs):
        self.quad.drawable.shader.set_uniform("u_time", rs.time)
        self.quad.drawable.shader.set_uniform("u_tex1", 0)
        self.quad.drawable.shader.set_uniform("u_tex2", 1)
        self.quad.draw(rs.render_width, rs.render_height)


class GeometryNode(RenderNode):

    def __init__(self, name):
        super().__init__(name)
        self.mesh = TriangleMesh()
        self.mesh.add_quad((-1,-1,0), (1,-1,0), (1,1,0), (-1,1,0))
        self.drawable = self.mesh.create_drawable()
        self.drawable.shader.set_fragment_source("""
        #version 130
        #line 89
        uniform sampler2D u_tex1;
        uniform sampler2D u_tex2;
        
        in vec4 v_pos;
        in vec4 v_color;
        in vec3 v_normal;
        in vec2 v_texcoord;
        
        out vec4 fragColor;
        
        void main() {
            vec4 col = texture(u_tex1, v_texcoord);
            fragColor = col;
        }
        """)

    def release(self):
        self.drawable.release()

    def render(self, rs):
        proj = glm.ortho(-3, 3, -3, 3, -3, 3)
        proj = glm.rotate(proj, rs.time, (0,0,1))
        self.drawable.shader.set_uniform("u_time", rs.time)
        self.drawable.shader.set_uniform("u_tex1", 0)
        self.drawable.shader.set_uniform("u_tex2", 1)
        self.drawable.shader.set_uniform("u_projection", proj)
        self.drawable.draw()


class RenderGraphWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(RenderGraphWindow, self).__init__(*args, **kwargs)

        self.render_settings = RenderSettings(320, 200)

        self.graph = RenderGraph()

        self.graph.add_node(ColorNode("color"))
        self.graph.add_node(GridNode("grid"))
        self.graph.add_node(CombineNode("mul", "*"))
        self.graph.add_node(CombineNode("add", "+"))
        self.graph.add_node(GeometryNode("geom"))

        self.graph.connect("color", 0, "mul", 0)
        self.graph.connect("grid", 0, "mul", 1)
        self.graph.connect("mul", 0, "geom", 0)
        self.graph.connect("mul", 0, "add", 0)
        self.graph.connect("geom", 0, "add", 1)

        self.pipeline = self.graph.create_pipeline()
        print(self.pipeline.stages)
        self.pipeline.dump()

        self.start_time = time.time()
        pyglet.clock.schedule_interval(self.update, 1.0 / 60.0)
        pyglet.clock.set_fps_limit(60)

    def update(self, dt):
        pass

    def on_draw(self):
        self.clear()
        self.render_settings.screen_width = self.width
        self.render_settings.screen_height = self.height
        self.render_settings.time = time.time() - self.start_time

        self.pipeline.render(self.render_settings)

        self.pipeline.render_to_screen(self.render_settings)


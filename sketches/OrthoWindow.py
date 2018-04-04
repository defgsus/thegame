import time
import pyglet
import glm
from pyglet.gl import *
from lib.opengl.core.Shader import *
from lib.opengl.core.Texture2D import Texture2D
from lib.opengl.core.Framebuffer2D import Framebuffer2D
from lib.opengl.ScreenQuad import ScreenQuad

from lib.geom.TriangleMesh import TriangleMesh

frag_src = """#version 130
#line 11
uniform sampler2D u_tex1;
uniform float u_time;

in vec4 v_pos;
in vec3 v_normal;
in vec2 v_texcoord;

out vec4 fragColor;

vec3 poscol(in vec4 p) {
    float z = p.z*4.;
    return vec3(1.-z, .3+z, 0.);
}

void main() {
    vec4 tex = texture2D(u_tex1, v_texcoord);
    
    vec3 lightpos = vec3(sin(u_time/3.)*.3, sin(u_time/5.)*.5, .3);
    vec3 lightnorm = normalize(lightpos - v_pos.xyz);
    float lightdot = max(0., dot(v_normal, lightnorm));
    
    vec2 grid = mod(v_pos.xy*10., 1.);
    vec3 col = vec3(0);
    float g = smoothstep(.02, .0, .49-abs(grid.x-.5));
    g = max(g, smoothstep(.02, .0, .49-abs(grid.y-.5)));
    col += 1.-g;
    
    col = mix(col, poscol(v_pos), .4);
    col = mix(col, v_normal*.5+.5, .5);
    col = mix(col, tex.rgb, 1.);  
    col *= clamp(lightdot, .4, 1.);
    
    //col += sin(u_time+v_pos.x);
    //col = mix(col, vec3(v_texcoord, 0.), .9);
    //col = vec3(lightdot);  
    fragColor = vec4(col, 1);
}
"""

HEIGHTMAP = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 1, 2, 2, 2, 2, 2, 0, 0],
    [0, 0, 1, 2, 1, 1, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]


class OrthoWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(OrthoWindow, self).__init__(*args, vsync=True, **kwargs)

        self.mesh = TriangleMesh()
        #self.mesh = TriangleHashMesh()
        def heightmap(x, y):
            return HEIGHTMAP[max(0,min(9,y))][max(0,min(9,x))] / 10
            #return random.randrange(max(1,random.randrange(3)))/10
        self.mesh.create_height_map(10,10, heightmap, 1./10)
        self.drawable = self.mesh.get_drawable()
        self.drawable.shader.set_fragment_source(frag_src)
        self.texture = Texture2D()
        self.fbo = Framebuffer2D(self.width, self.height)
        self.quad = ScreenQuad()

        self.projection = "i"
        self._init_rotation()

        self.start_time = time.time()

        pyglet.clock.schedule_interval(self.update, 1.0 / 20.0)
        pyglet.clock.set_fps_limit(20)

    def update(self, dt):
        pass

    def on_draw(self):
        glDisable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        self.clear()

        if self.projection in "io":
            proj = glm.ortho(-.5,.5, .5,-.5, -2, 2)
        else:
            proj = glm.perspective(30., self.width / self.height, 0.01, 10.)
            proj = glm.translate(proj, (0,0,-1))
        proj = glm.rotate(proj, self.rotate_x, (1,0,0))
        proj = glm.rotate(proj, self.rotate_y, (0,1,0))
        proj = glm.rotate(proj, self.rotate_z, (0,0,1))
        #print(proj)

        if not self.texture.is_created():
            self.texture.create()
            self.texture.bind()
            #self.texture.upload_image("./assets/STEEL.BMP")
            #self.texture.upload_image("./assets/bluenoise.png")
            self.texture.upload_image("./assets/blueplate.png")
            #self.texture.upload([random.randrange(256) for x in range(16*16*3)], 16, input_type=GL_BYTE)

        if self.fbo:
            if self.fbo.is_created():
                if self.fbo.width != self.width or self.fbo.height != self.height:
                    self.fbo.release()
                    self.fbo = Framebuffer2D(self.width, self.height)

            if not self.fbo.is_created():
                self.fbo.create()

            self.fbo.bind()
            self.fbo.clear()
        self.drawable.shader.set_uniform("u_projection", proj)
        self.drawable.shader.set_uniform("u_time", time.time() - self.start_time)
        self.texture.bind()
        self.drawable.draw()
        if self.fbo:
            self.fbo.unbind()

            self.fbo.color_texture(0).bind()
            #self.fbo.depth_texture().bind()
            self.quad.draw(self.width, self.height)

        #OpenGlBaseObject.dump_instances()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.rotate_x += scroll_y / 30.

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.rotate_y += dx / 30.

    def on_text(self, text):
        if text == "o":
            self.projection = "o"
            self._init_rotation()
        if text == "i":
            self.projection = "i"
            self._init_rotation()
            self.rotate_z = glm.pi()/4
        if text == "p":
            self.projection = "p"
            self._init_rotation()

    def _init_rotation(self):
        self.rotate_x = glm.pi()/(3.3 if self.projection=="i" else 4)
        self.rotate_y = 0#-glm.pi()/4.
        self.rotate_z = 0
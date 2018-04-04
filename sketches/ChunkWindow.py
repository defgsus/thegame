import time
import pyglet
import glm
import math
from pyglet.gl import *
from lib.opengl import *

from lib.world import *

frag_src = """#version 130
#line 11
uniform sampler2D u_tex1;
uniform sampler2D u_tex2;
uniform sampler3D u_chunktex;

uniform float u_time;
uniform vec3 u_lightpos;

in vec4 v_pos;
in vec3 v_normal;
in vec2 v_texcoord;

out vec4 fragColor;

vec3 poscol(in vec4 p) {
    float z = p.z*4.;
    return vec3(1.-z, .3+z, 0.);
}

vec3 lighting(in vec3 lightpos, in vec3 pos, in vec3 normal) {
    vec3 lightnorm = normalize(lightpos - pos);
    float d = max(0., dot(normal, lightnorm));
    
    return clamp(vec3(d,d,pow(d,1.3)), .4, 1.);
}

void main() {
    vec4 tex = texture2D(u_tex1, v_texcoord);
        
    vec3 col = vec3(0);
    //col = mix(col, poscol(v_pos), .4);
    //col = mix(col, v_normal*.5+.5, .5);
    col = mix(col, tex.rgb, 1.);  
    col *= lighting(u_lightpos, v_pos.xyz, v_normal);
    
    //col = mix(col, texture2D(u_tex2, v_texcoord).xyz, .5);
    //col = mix(col, texture3D(u_chunktex, v_pos.xyz).xyz, .9);
    
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
    [0, 0, 0, 1, 1, 1, 0, 1, 0, 0],
    [0, 0, 1, 2, 2, 2, 2, 4, 1, 0],
    [0, 0, 1, 2, 1, 1, 0, 1, 0, 0],
    [0, 0, 1, 2, 1, 0, 0, 0, 0, 0],
    [0, 0, 1, 2, 1, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]


class ChunkWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(ChunkWindow, self).__init__(*args, vsync=True, **kwargs)

        self.tileset = Tileset(16, 16)
        self.tileset.load("./assets/tileset01.png")
        print(self.tileset)

        self.chunk = WorldChunk(self.tileset)
        self.chunk.from_heightmap(HEIGHTMAP)

        self.chunktex = None

        self.texture = Texture2D()
        self.mesh = self.chunk.create_mesh()
        self.drawable = self.mesh.get_drawable()
        self.drawable.shader.set_fragment_source(frag_src)

        self.texture2 = Texture2D()

        if 1:
            self.fbo = Framebuffer2D(self.width, self.height)
            self.quad = ScreenQuad()
        else:
            self.fbo = None

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

        sc = self.chunk.num_x / 2

        if self.projection in "io":
            proj = glm.ortho(-sc,sc, sc,-sc, -sc*2, sc*2)
        else:
            proj = glm.perspective(30., self.width / self.height, 0.01, 10.)
            proj = glm.translate(proj, (0,0,-1))
        proj = glm.rotate(proj, self.rotate_x, (1,0,0))
        proj = glm.rotate(proj, self.rotate_y, (0,1,0))
        proj = glm.rotate(proj, self.rotate_z, (0,0,1))
        proj = glm.translate(proj, (-self.chunk.num_x/2, -self.chunk.num_y/2, 0))
        #print(proj)

        if self.chunktex is None:
            self.chunktex = self.chunk.create_texture3d()

        if not self.texture.is_created():
            self.texture.create()
            self.texture.bind()
            #self.texture.upload_image("./assets/bluenoise.png")
            #self.texture.upload_image("./assets/blueplate.png")
            self.texture.upload_image_PIL(self.tileset.image)
            #self.texture.upload([random.randrange(256) for x in range(16*16*3)], 16, input_type=GL_BYTE)

        if not self.texture2.is_created():
            self.texture2.create()
            self.texture2.bind()
            self.texture2.upload_image("./assets/happystone.png")

        if self.fbo:
            if self.fbo.is_created():
                if self.fbo.width != self.width or self.fbo.height != self.height:
                    self.fbo.release()
                    self.fbo = Framebuffer2D(self.width, self.height)

            if not self.fbo.is_created():
                self.fbo.create()

            self.fbo.bind()
            self.fbo.clear()

        ti = time.time() - self.start_time

        lightpos = (
           math.sin(ti/2.)*self.chunk.num_x/2.,
           math.sin(ti/3.)*self.chunk.num_y/2.,
           self.chunk.num_z
        )
        self.drawable.shader.set_uniform("u_projection", proj)
        self.drawable.shader.set_uniform("u_time", ti)
        self.drawable.shader.set_uniform("u_lightpos", lightpos)
        self.drawable.shader.set_uniform("u_tex1", 0)
        self.drawable.shader.set_uniform("u_tex2", 1)
        self.drawable.shader.set_uniform("u_chunktex", 2)

        self.texture.set_active_texture(0)
        self.texture.bind()
        self.texture.set_active_texture(1)
        self.texture2.bind()
        self.texture.set_active_texture(2)
        self.chunktex.bind()
        self.drawable.draw()
        self.texture.set_active_texture(0)

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
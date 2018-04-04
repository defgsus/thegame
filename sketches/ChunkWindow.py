import time
import pyglet
import glm
import math
from pyglet.gl import *
from lib.opengl.VertexArrayObject import *
from lib.opengl.Shader import *
from lib.opengl.Drawable import Drawable
from lib.opengl.Texture2D import Texture2D
from lib.opengl.Framebuffer2D import Framebuffer2D
from lib.opengl.ScreenQuad import ScreenQuad

from lib.world.WorldChunk import WorldChunk
from lib.world.Tileset import Tileset

from lib.geom.TriangleMesh import TriangleHashMesh, TriangleMesh

frag_src = """#version 130
#line 11
uniform sampler2D u_tex1;
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

void main() {
    vec4 tex = texture2D(u_tex1, v_texcoord);
    
    vec3 lightnorm = normalize(u_lightpos - v_pos.xyz);
    float lightdot = max(0., dot(v_normal, lightnorm));
    
    vec3 col = vec3(0);
    //col = mix(col, poscol(v_pos), .4);
    //col = mix(col, v_normal*.5+.5, .5);
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

        self.texture = Texture2D()
        self.mesh = self.chunk.create_mesh()
        self.drawable = self.mesh.get_drawable()
        self.drawable.shader.set_fragment_source(frag_src)

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

        if not self.texture.is_created():
            self.texture.create()
            self.texture.bind()
            #self.texture.upload_image("./assets/STEEL.BMP")
            #self.texture.upload_image("./assets/bluenoise.png")
            #self.texture.upload_image("./assets/blueplate.png")
            self.texture.upload_image_PIL(self.tileset.image)
            import random
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

        ti = time.time() - self.start_time

        lightpos = (
           math.sin(ti/2.)*self.chunk.num_x/2.,
           math.sin(ti/3.)*self.chunk.num_y/2.,
           self.chunk.num_z
        )
        self.drawable.shader.set_uniform("u_projection", proj)
        self.drawable.shader.set_uniform("u_time", ti)
        self.drawable.shader.set_uniform("u_lightpos", lightpos)

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
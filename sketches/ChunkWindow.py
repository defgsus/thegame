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
uniform vec3 u_chunksize;

in vec4 v_pos;
in vec3 v_normal;
in vec2 v_texcoord;

out vec4 fragColor;

float voxel_at(in vec3 pos) {
    if (any(lessThan(pos, vec3(1))) || any(greaterThanEqual(pos, u_chunksize)))
        return 0.;
    return texelFetch(u_chunktex, ivec3(pos+.5), 0).x;
}

float voxel_density(in vec3 pos) {
    return texture(u_chunktex, (pos+vec3(0,0,.5)) / u_chunksize).y;
}

// Inigo Quilez, Reinder Nijhoff, https://www.shadertoy.com/view/4ds3WS
float voxel_shadow_ray(in vec3 ro, in vec3 rd) {

    vec3 pos = floor(ro);
    vec3 ri = 1.0/rd;
    vec3 rs = sign(rd);
    vec3 dis = (pos-ro + 0.5 + rs*0.5) * ri;

    float res = 1.0;

    for(int i=0; i<15; i++) 
    {
        if (any(lessThan(pos, vec3(0))) || any(greaterThanEqual(pos, u_chunksize))) { break; }
        if (voxel_at(pos) > 0.) { res *= 0.0; break; }
        
        //res -= voxel_density(pos+vec3(0,0,1))*.1;
        
        vec3 mm = step(dis.xyz, dis.yxy) * step(dis.xyz, dis.zzx);
        dis += mm * rs * ri;
        pos += mm * rs;
    }

    return res;
}


vec3 lighting(in vec3 lightpos, in vec3 pos, in vec3 normal) {
    vec3 lightnorm = normalize(lightpos - pos);
    float d = max(0., dot(normal, lightnorm));
    if (d > 0.)
    {
        d *= voxel_shadow_ray(pos+0.01*normal, lightnorm);
    }
    
    return clamp(vec3(d,d,pow(d,1.3)), .3, 1.);
}

void main() {
    vec4 tex = texture2D(u_tex1, v_texcoord);
        
    vec3 col = vec3(0);
    //col = mix(col, poscol(v_pos), .4);
    //col = mix(col, v_normal*.5+.5, .5);
    col = mix(col, tex.rgb, 1.);  
    col *= lighting(u_lightpos, v_pos.xyz, v_normal);
    
    //col.x += v_pos.y/10.;
    //col = mix(col, vec3(voxel_at(v_pos.xyz-v_normal*.01)), .8);
    //col = mix(col, texture2D(u_tex2, v_texcoord).xyz, .5);
    //col += texture(u_chunktex, v_pos.xyz*2.1).xyz;
    
    //col += sin(u_time+v_pos.x);
    //col = mix(col, vec3(v_texcoord, 0.), .9);
    //col = vec3(lightdot);  
    
    col *= vec3(1. - voxel_density(v_pos.xyz));
    
    fragColor = vec4(col, 1);
}
"""

HEIGHTMAP2 = [
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

HEIGHTMAP1 = [
    [4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [3, 0, 5, 0, 0, 0, 0, 0, 0, 0],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [3, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [2, 0, 0, 1, 1, 1, 0, 1, 0, 0],
    [3, 0, 1, 2, 2, 2, 2, 4, 1, 0],
    [2, 0, 1, 2, 1, 1, 0, 1, 0, 0],
    [0, 0, 1, 2, 1, 0, 0, 0, 0, 0],
    [0, 0, 1, 2, 1, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

_ = 0
HEIGHTMAP = [
    [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, _, _, _],
    [_, _, 2, _, _, _, _, _, _, _, _, _, _, 2, _, _],
    [_, _, 3, _, _, 1, 2, 3, 2, 1, _, _, _, 3, _, _],
    [_, _, 2, _, _, 1, _, _, _, 1, _, _, _, 2, _, _],
    [_, _, 3, _, _, 1, _, _, _, 1, _, _, _, 3, _, _],
    [_, _, 2, _, _, _, _, _, _, _, _, _, _, 2, _, _],
    [_, _, 7, 6, 7, _, _, _, _, _, _, 7, 6, 7, _, _],
    [_, _, 6, 4, 6, _, _, _, _, _, _, 6, 5, 6, _, _],
    [_, _, 7, 6, 7, 2, 3, _, _, 3, 2, 7, 6, 7, _, _],
    [_, _, _, _, _, _, 1, _, _, 1, _, _, _, _, _, _],
    [_, _, _, _, _, _, 1, _, _, 1, _, _, _, _, _, _],
    [_, _, _, _, 4, 4, _, _, _, _, 4, 4, _, _, _, _],
    [_, _, _, _, 4, 4, _, _, _, _, 4, 4, _, _, _, _],
    [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
]


def gen_heightmap(w=16, h=32):
    import random
    rows = []
    for y in range(h):
        row = []
        for x in range(w):
            h = 0
            h += (math.sin(x/5.)+math.cos(y/7))*2.6
            if random.randrange(4) == 0:
                h = random.randrange(5)
            row.append(max(0, int(h)))
        rows.append(row)
    return rows


class ChunkWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(ChunkWindow, self).__init__(
            *args,
            #width=800, height=600,
            vsync=True, **kwargs)

        self.tileset = Tileset(16, 16)
        self.tileset.load("./assets/tileset01.png")
        print(self.tileset)

        self.chunk = WorldChunk(self.tileset)
        #self.chunk.from_heightmap(gen_heightmap())
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

        self.srotate_x = 0.
        self.srotate_y = 0.
        self.srotate_z = 0.
        self.projection = "o"
        self._init_rotation()
        self._calc_projection()
        self.sprojection_matrix = self.projection_matrix

        self.start_time = time.time()

        pyglet.clock.schedule_interval(self.update, 1.0 / 60.0)
        pyglet.clock.set_fps_limit(60)

    def update(self, dt):
        d = dt * 5.
        self.srotate_x += d * (self.rotate_x-self.srotate_x)
        self.srotate_y += d * (self.rotate_y-self.srotate_y)
        self.srotate_z += d * (self.rotate_z-self.srotate_z)
        d = dt * 3.
        self.sprojection_matrix += d * (self.projection_matrix - self.sprojection_matrix)
        pass

    def on_draw(self):
        glDisable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        self.clear()

        self._calc_projection()

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
           (math.sin(ti/3.)+2.)*self.chunk.num_y/2.,
           self.chunk.num_z+1
        )
        self.drawable.shader.set_uniform("u_projection", self.sprojection_matrix)
        self.drawable.shader.set_uniform("u_time", ti)
        self.drawable.shader.set_uniform("u_lightpos", lightpos)
        self.drawable.shader.set_uniform("u_tex1", 0)
        self.drawable.shader.set_uniform("u_tex2", 1)
        self.drawable.shader.set_uniform("u_chunktex", 2)
        self.drawable.shader.set_uniform("u_chunksize", self.chunk.size())

        self.texture.set_active_texture(0)
        self.texture.bind()
        self.texture.set_active_texture(1)
        self.texture2.bind()
        self.texture.set_active_texture(2)
        self.chunktex.bind()
        self.texture.set_active_texture(0)

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
        if text == "f":
            self.set_fullscreen(not self.fullscreen)

    def _calc_projection(self):
        sc = min(16, self.chunk.num_x) / 1.3
        asp = self.width / self.height

        if self.projection == "i":
            ysc = sc/asp
            proj = glm.ortho(sc,-sc, ysc,-ysc, -sc*4, sc*4)
        elif self.projection == "o":
            ysc = sc/asp * .75
            proj = glm.ortho(sc,-sc, ysc,-ysc, -sc*4, sc*4)
        else:
            #proj = glm.frustum(-1,1, -1,1, 0.01, 3)
            proj = glm.perspective(30, self.width / self.height, 0.01, sc*3.)
            proj = glm.translate(proj, (0,0,-10))

        proj = glm.rotate(proj, self.srotate_x, (1,0,0))
        proj = glm.rotate(proj, self.srotate_y, (0,1,0))
        proj = glm.rotate(proj, self.srotate_z, (0,0,1))
        proj = glm.translate(proj, (-self.chunk.num_x/2, -self.chunk.num_y/2,
                                    [-3,-2,-4]["oip".index(self.projection)]))
        #print(proj)
        self.projection_matrix = proj

    def _init_rotation(self):
        self.rotate_x = glm.pi()/(3.3 if self.projection=="i" else 4)
        self.rotate_y = 0#-glm.pi()/4.
        self.rotate_z = 0
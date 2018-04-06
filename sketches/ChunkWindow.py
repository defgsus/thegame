import time
import pyglet
import glm
import math
from pyglet.gl import *
from lib.opengl import *

from lib.world import *

from .ChunkWindow_shader import frag_src


HEIGHTMAP2 = [
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 5, 1, 1, 0, 0, 0, 0],
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
    [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, 2, _, _, _, _, _, _, 3, _, _, _, 2, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, 3, _, _, _, _, _, _, 2, _, _, _, 3, _, _, _, 1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 1, _, _, _],
    [_, _, 2, _, _, _, _, _, _, 3, _, 1, _, 2, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, 3, 2, 2, 2, _, _, _, 2, _, 1, _, 3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, 2, _, _, _, _, _, _, 3, _, 2, 3, 2, _, _, _, _, _, 3, _, _, _, _, _, 2, _, _, _, _, _, _, _],
    [_, _, 3, _, _, _, _, _, _, _, _, 1, _, 3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, 2, _, _, _, _, _, _, _, _, 1, _, 2, _, _, _, _, _, _, _, _, 6, _, _, _, _, _, _, _, _, _, _],
    [_, _, 3, _, _, _, _, _, _, _, _, _, _, 3, _, _, _, 5, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, 3, _, _, 1, 2, 3, 2, 1, _, _, _, 3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 1, _, _, _, _],
    [_, _, 2, _, _, 1, _, _, _, 1, _, _, _, 2, _, 2, _, _, _, _, 4, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, 3, _, _, 1, _, _, _, 1, _, _, _, 3, _, _, _, _, _, _, _, _, _, 7, _, _, _, _, _, _, _, _, _],
    [_, _, 2, _, _, _, _, _, _, _, _, _, _, 2, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, 7, 6, 7, _, _, _, _, _, _, 7, 6, 7, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, 6, 4, 6, _, _, _, _, _, _, 6, 5, 6, _, _, _, _, _, _, _, _, 2, _, _, _, _, _, _, _, _, _, _],
    [_, _, 7, 6, 7, 2, 3, _, _, 3, 2, 7, 6, 7, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, _, _, _, _, 1, _, _, 1, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, _, _, _, _, 1, _, _, 1, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, _, _, 4, 4, _, _, _, _, 4, 4, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, _, _, 4, 4, _, _, _, _, 4, 4, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
    [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],
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

        self.keys = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keys)

        self.tileset = Tileset(16, 16)
        self.tileset.load("./assets/tileset01.png")
        print(self.tileset)

        # ---- world chunk ----

        self.chunk = WorldChunk(self.tileset)
        #self.chunk.from_heightmap(gen_heightmap())
        self.chunk.from_heightmap(HEIGHTMAP)

        # voxel texture
        self.chunktex = None

        # distance map
        self.vdf_scale = 1
        self.vdf = self.chunk.create_voxel_distance_field(self.vdf_scale)
        if 1:
            self.vdf.calc_distances()
            self.vdf.save_json("./temp/vdf.json")
        else:
            self.vdf.load_json("./temp/vdf.json")
        self.vdf_tex = None

        # mesh and texture
        self.texture = Texture2D()
        self.mesh = self.chunk.create_mesh()
        self.drawable = self.mesh.get_drawable()
        self.drawable.shader.set_fragment_source(frag_src)

        self.texture2 = Texture2D()

        # post-fx
        if 1:
            self.fbo = Framebuffer2D(self.width, self.height)
            self.quad = ScreenQuad()
        else:
            self.fbo = None

        # player
        self.player_pos = glm.vec3(10, 15, 10) + .5
        self.splayer_pos = glm.vec3(self.player_pos)

        # projection
        self.zoom = 0.
        self.szoom = 0.
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
        self.check_keys(dt)
        newpos = self.player_pos + min(1,dt*5) * glm.vec3(0,0,-1)
        if self.chunk.block(int(newpos.x), int(newpos.y), int(newpos.z-.5)).space_type == 0:
            self.player_pos = newpos

        d = dt * 5.
        self.szoom += d + (self.zoom - self.szoom)
        self.srotate_x += d * (self.rotate_x-self.srotate_x)
        self.srotate_y += d * (self.rotate_y-self.srotate_y)
        self.srotate_z += d * (self.rotate_z-self.srotate_z)
        self.splayer_pos += d * (self.player_pos - self.splayer_pos)
        d = dt * 3.
        self.sprojection_matrix += d * (self.projection_matrix - self.sprojection_matrix)

    def check_keys(self, dt):
        dir_mapping = {
            # TODO: projection/mapping/coord-system is completely off
            pyglet.window.key.LEFT: glm.vec3(1,0,0),
            pyglet.window.key.RIGHT: glm.vec3(-1,0,0),
            pyglet.window.key.UP: glm.vec3(0,-1,0),
            pyglet.window.key.DOWN: glm.vec3(0,1,0),
            pyglet.window.key.SPACE: glm.vec3(0,0,4),
        }
        for symbol in dir_mapping:
            if self.keys[symbol]:
                dir = dir_mapping[symbol]
                #dir = self.projection_matrix * glm.vec4(dir, 0.)
                #dir = dir.xyz;
                newpos = self.player_pos + dir * min(1, dt*10.)
                if self.chunk.block(int(newpos.x), int(newpos.y), int(newpos.z)).space_type == 0:
                    self.player_pos = newpos

    def on_draw(self):
        glDisable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        self.clear()

        self._calc_projection()

        if self.chunktex is None:
            self.chunktex = self.chunk.create_texture3d()

        if self.vdf_tex is None:
            self.vdf_tex = self.vdf.create_texture3d("vdf")
            print(self.vdf_tex)

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
        self.drawable.shader.set_uniform("u_vdf_tex", 3)
        self.drawable.shader.set_uniform("u_vdf_size", self.vdf.size())
        self.drawable.shader.set_uniform("u_vdf_scale", self.vdf_scale)
        self.drawable.shader.set_uniform("u_player_pos", (self.splayer_pos))

        self.texture.set_active_texture(0)
        self.texture.bind()
        self.texture.set_active_texture(1)
        self.texture2.bind()
        self.texture.set_active_texture(2)
        self.chunktex.bind()
        self.texture.set_active_texture(3)
        self.vdf_tex.bind()
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

    def on_mouse_press(self, x, y, button, modifiers):
        ro, rd = self.get_ray(x, y)
        print(ro, rd)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.close()

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
        if text == "e":
            self.projection = "e"
            self._init_rotation()
        if text == "f":
            self.set_fullscreen(not self.fullscreen)
        if text == "+":
            self.zoom += 1.
        if text == "-":
            self.zoom -= 1.

    def get_uv(self, x, y):
        return ((x / self.width * 2. - 1.) * self.width / self.height,
                y / self.height * 2. - 1.)

    def get_ray(self, x, y):
        uv = self.get_uv(x, y)
        ro = glm.vec3(self.projection_matrix[3])
        m = glm.mat4(self.projection_matrix)
        m[3][0] = 0
        m[3][1] = 0
        m[3][2] = 0
        rd = m * glm.vec4(glm.normalize(glm.vec3(uv[0], uv[1], -1.2)), 0)
        return (ro, rd)

    def _calc_projection(self):
        sc = min(16, self.chunk.num_x) / 1.3
        asp = self.width / self.height

        if self.projection == "i":
            ysc = sc/asp
            proj = glm.ortho(sc,-sc, ysc,-ysc, -sc*4, sc*4)
        elif self.projection == "o":
            ysc = sc/asp * .75
            proj = glm.ortho(sc,-sc, ysc,-ysc, -sc*4, sc*4)
        elif self.projection == "p":
            #proj = glm.frustum(-1,1, -1,1, 0.01, 3)
            proj = glm.perspective(30, self.width / self.height, 0.01, sc*3.)
            proj = glm.translate(proj, (0,0,-5))
        else:  # "e"
            proj = glm.perspective(30, self.width / self.height, 0.01, sc*3.)
            proj = glm.translate(proj, (0,0,0))

        proj = glm.rotate(proj, self.srotate_x, (1,0,0))
        proj = glm.rotate(proj, self.srotate_y, (0,1,0))
        proj = glm.rotate(proj, self.srotate_z, (0,0,1))
        proj = glm.translate(proj, (0,0,#-self.chunk.num_x/2, -self.chunk.num_y/2,
                                    [-3,-2,-4,-1]["oipe".index(self.projection)]))

        proj = glm.scale(proj, glm.vec3(1.+self.zoom/10.))
        proj = glm.translate(proj, -self.splayer_pos)

        #print(proj)
        self.projection_matrix = proj

    def _init_rotation(self):
        self.rotate_x = glm.pi()/(3.3 if self.projection=="i" else 4)
        if self.projection == "e":
            self.rotate_x = glm.pi()/2.
        self.rotate_y = 0#-glm.pi()/4.
        self.rotate_z = 0
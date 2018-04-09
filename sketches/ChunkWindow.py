import time
import pyglet
import glm
import math
from pyglet.gl import *
from lib.opengl import *
from lib.geom import *
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

        self.edit_mode = False
        self.debug_view = 0

        self.keys = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keys)

        self.tileset = Tileset(16, 16)
        #self.tileset.load("./assets/tileset01.png")
        self.tileset.load("./assets/tileset02.png")
        print(self.tileset)

        # ---- world chunk ----

        self.chunk = WorldChunk(self.tileset)
        self.chunk_changed = False
        if 0:
            #self.chunk.from_heightmap(gen_heightmap())
            self.chunk.from_heightmap(HEIGHTMAP, do_flip_y=True)
        else:
            tiled = TiledImport()
            self.chunk.from_tiled("./assets/tiled/level01.json")

        # click in world
        self.hit_voxel = (-1,-1,-1)
        self.click_mesh = LineMesh()
        self.click_mesh_changed = False
        self.click_drawable = Drawable()

        # voxel texture
        self.chunktex = None

        # distance map
        self.vdf_scale = 1
        self.vdf = self.chunk.create_voxel_distance_field(self.vdf_scale)
        self.vdf_tex = None

        # mesh and texture
        self.texture = Texture2D()
        self.mesh = self.chunk.create_mesh()
        self.drawable = self.mesh.create_drawable()
        self.drawable.shader.set_fragment_source(frag_src)

        self.texture2 = Texture2D()

        # edit mesh
        self.edit_drawable = Drawable()
        self.cur_edit_voxel = (-1,-1,-1)

        # post-fx
        if 1:
            self.fbo = Framebuffer2D(self.width, self.height)
            self.quad = ScreenQuad()
        else:
            self.fbo = None

        # player
        self.player_pos = glm.vec3(2, 2, 10) + .5
        self.splayer_pos = glm.vec3(self.player_pos)

        # projection
        self.projection = WorldProjection(self.width, self.height, WorldProjection.P_ISOMETRIC)
        self.projection.update(.4)

        # time(r)
        self.start_time = time.time()
        pyglet.clock.schedule_interval(self.update, 1.0 / 60.0)
        pyglet.clock.set_fps_limit(60)

    def update(self, dt):
        self.check_keys(dt)
        newpos = self.player_pos + min(1,dt*5) * glm.vec3(0,0,-1)
        if self.chunk.block(int(newpos.x), int(newpos.y), int(newpos.z-.5)).space_type == 0:
            self.player_pos = newpos

        d = min(1, dt*5)
        self.splayer_pos += d * (self.player_pos - self.splayer_pos)

        self.projection.width = self.width
        self.projection.height = self.height
        self.projection.user_transformation = glm.translate(glm.mat4(1), -self.splayer_pos)
        self.projection.update(dt)

    def check_keys(self, dt):
        dir_mapping = {
            pyglet.window.key.LEFT: glm.vec3(-1,0,0),
            pyglet.window.key.RIGHT: glm.vec3(1,0,0),
            pyglet.window.key.UP: glm.vec3(0,1,0),
            pyglet.window.key.DOWN: glm.vec3(0,-1,0),
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
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.clear()

        if self.chunktex is None:
            self.chunktex = self.chunk.create_texture3d()

        if self.chunk_changed:
            self.chunk_changed = False
            self.chunk.update_texture3d(self.chunktex)
            self.mesh = self.chunk.create_mesh()
            self.mesh.update_drawable(self.drawable)

        if self.vdf_tex is None:
            self.vdf_tex = self.vdf.create_texture3d("vdf")
            print(self.vdf_tex)

        if not self.texture.is_created():
            self.texture.create()
            self.texture.bind()
            #self.texture.upload_image("./assets/bluenoise.png")
            #self.texture.upload_image("./assets/blueplate.png")
            self.texture.upload_image_PIL(self.tileset.image, do_flip_y=True)
            #self.texture.upload([random.randrange(256) for x in range(16*16*3)], 16, input_type=GL_BYTE)

        if not self.texture2.is_created():
            self.texture2.create()
            self.texture2.bind()
            self.texture2.upload_image("./assets/happystone.png")

        do_postproc = self.fbo and not self.edit_mode

        if do_postproc:
            if self.fbo.is_created():
                if self.fbo.width != self.width or self.fbo.height != self.height:
                    self.fbo.release()
                    self.fbo = Framebuffer2D(self.width, self.height)

            if not self.fbo.is_created():
                self.fbo.create()

            self.fbo.bind()
            self.fbo.clear()

        ti = time.time() - self.start_time

        proj = self.projection.matrix

        lightpos = glm.vec3(self.hit_voxel) + (.5,.5,1.5)
        lightamt = .94+.06*math.sin(ti*2.)
        self.drawable.shader.set_uniform("u_projection", proj)
        self.drawable.shader.set_uniform("u_time", ti)
        self.drawable.shader.set_uniform("u_lightpos", glm.vec4(lightpos, lightamt))
        self.drawable.shader.set_uniform("u_tex1", 0)
        self.drawable.shader.set_uniform("u_tex2", 1)
        self.drawable.shader.set_uniform("u_chunktex", 2)
        self.drawable.shader.set_uniform("u_chunksize", self.chunk.size())
        self.drawable.shader.set_uniform("u_vdf_tex", 3)
        self.drawable.shader.set_uniform("u_vdf_size", self.vdf.size())
        self.drawable.shader.set_uniform("u_vdf_scale", self.vdf_scale)
        self.drawable.shader.set_uniform("u_player_pos", self.splayer_pos)
        self.drawable.shader.set_uniform("u_hit_voxel", self.hit_voxel)
        self.drawable.shader.set_uniform("u_debug_view", self.debug_view)

        self.texture.set_active_texture(0)
        self.texture.bind()
        self.texture.set_active_texture(1)
        self.texture2.bind()
        self.texture.set_active_texture(2)
        self.chunktex.bind()
        self.texture.set_active_texture(3)
        self.vdf_tex.bind()
        self.texture.set_active_texture(0)

        # main scene
        self.drawable.draw()

        # edit mesh
        if self.edit_mode and not self.edit_drawable.is_empty():
            self.edit_drawable.shader.set_uniform("u_projection", proj)
            self.edit_drawable.draw()

        # click debugger
        if self.click_mesh_changed:
            self.click_mesh_changed = False
            self.click_mesh.update_drawable(self.click_drawable)

        if not self.click_drawable.is_empty():
            self.click_drawable.shader.set_uniform("u_projection", proj)
            self.click_drawable.draw()

        # coordinate system
        if 0:
            if not hasattr(self, "coord_sys"):
                self.coord_sys = CoordinateGrid(20)
            self.coord_sys.drawable.shader.set_uniform("u_projection", proj)
            self.coord_sys.draw()

        # post-proc

        if do_postproc:
            self.fbo.unbind()

            self.fbo.color_texture(0).bind()
            #self.fbo.depth_texture().bind()
            self.quad.draw(self.width, self.height)

        #OpenGlBaseObject.dump_instances()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.projection._rotation[0] -= scroll_y / 30.

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.projection._rotation[1] += dx / 30.

    def on_mouse_press(self, x, y, button, modifiers):
        import random
        ro, rd = self.get_ray(x, y)
        if 0:
            rg = ro + 100 * rd
            for i in range(10):
                ofs = tuple(random.uniform(-.04, .04) for x in range(3))
                self.click_mesh.add_line(ro+ofs, rg+ofs)
            self.click_mesh_changed = True

        t, hit = self.chunk.cast_voxel_ray(ro, rd, 1000)
        if hit:
            pos = glm.floor(ro + t * rd)
            self.hit_voxel = pos
            pos = tuple(int(x) for x in pos)
            block = self.chunk.block(*pos)
            print(hit, t, pos, block.texture)
            if 0:
                block.space_type = 1
                block.texture = 40
                self.chunk_changed = True

    def on_mouse_motion(self, x, y, dx, dy):
        if not self.edit_mode:
            return
        ro, rd = self.get_ray(x, y)
        t, hit = self.chunk.cast_voxel_ray(ro, rd, 300)
        hit_voxel = tuple(int(x) for x in (ro+t*rd)) if hit else (-1,-1,-1)
        if hit_voxel != self.cur_edit_voxel:
            self.edit_drawable.clear()
            if hit:
                pos = glm.floor(ro+t*rd)+.5
                mesh = LineMesh()
                mesh.add_cube(pos, 1.1)
                mesh.update_drawable(self.edit_drawable)


    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.close()
        elif symbol == pyglet.window.key.F4:
            self.edit_mode = not self.edit_mode

    def on_text(self, text):
        if text in self.projection.PROJECTIONS:
            self.projection.init(text)
        if text == "f":
            self.set_fullscreen(not self.fullscreen)
        if text == "+":
            self.projection.zoom += 1.
        if text == "-":
            self.projection.zoom -= 1.
        if text == "d":
            self.debug_view = (self.debug_view + 1) % 2

    def get_ray(self, x, y):
        return self.projection.screen_to_ray(x, y)

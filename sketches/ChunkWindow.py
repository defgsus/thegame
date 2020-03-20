import time
import pyglet
import glm
import math
from pyglet.gl import *
from lib.opengl import *
from lib.geom import *
from lib.world import *
# from lib.world.render.ChunkRenderer_shader import vert_src, frag_src
from lib.ai import *


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

        self.tileset = Tileset.from_image(16, 16, "./assets/tileset02.png")
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
        self.texture = None
        self.mesh = self.chunk.create_mesh()
        self.drawable = self.mesh.create_drawable()
        #self.drawable.shader.set_vertex_source(vert_src)
        #self.drawable.shader.set_fragment_source(frag_src)

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
        self.agents = Agents(self.chunk)
        self.agents.create_agent("player", "./assets/pokeson.png")
        self.agents["player"].set_position(glm.vec3(2, 2, 10) + .5)

        # other guy
        follow = "player"
        for i in range(5):
            name = "other%s" % i
            self.agents.create_agent(name, "./assets/pokeson2.png")
            self.agents[name].set_position(glm.vec3(10, 15, 10) + .5)
            self.agents.set_follow(name, follow)
            follow = name

        # projection
        self._projection = WorldProjection(self.width, self.height, WorldProjection.P_ISOMETRIC)
        self._projection.update(.4)

        # time(r)
        self.start_time = time.time()
        pyglet.clock.schedule_interval(self.update, 1.0 / 60.0)
        # pyglet.clock.set_fps_limit(60)

    def update(self, dt):
        self.check_keys(dt)

        self.agents.update(dt)

        self._projection.width = self.width
        self._projection.height = self.height
        self._projection.user_transformation = glm.translate(glm.mat4(1), -self.agents["player"].sposition)
        self._projection.update(dt)

    def check_keys(self, dt):
        dir_mapping = {
            pyglet.window.key.LEFT: glm.vec3(-1,0,0),
            pyglet.window.key.RIGHT: glm.vec3(1,0,0),
            pyglet.window.key.UP: glm.vec3(0,1,0),
            pyglet.window.key.DOWN: glm.vec3(0,-1,0),
            #pyglet.window.key.SPACE: glm.vec3(0,0,1),
        }
        sum_dir = glm.vec3(0)
        num = 0
        for symbol in dir_mapping:
            if self.keys[symbol]:
                dir = dir_mapping[symbol]
                if self._projection.projection == self._projection.P_ISOMETRIC:
                    dir = glm.vec3(glm.rotate(glm.mat4(1), -glm.pi()/4., (0,0,1)) * glm.vec4(dir, 0))
                #dir *= min(1, dt*10.)
                sum_dir += dir
                num += 1
        if num:
            self.agents["player"].move(sum_dir / num * 1.5)

        if self.keys[pyglet.window.key.SPACE]:
            self.agents["player"].jump()

    def on_draw(self):
        glDisable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glDepthMask(True)
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

        if self.texture is None:
            self.texture = self.tileset.create_texture2d()
            #self.texture.upload_image("./assets/bluenoise.png")
            #self.texture.upload_image("./assets/blueplate.png")
            #self.texture.upload_image_PIL(self.tileset.image, do_flip_y=True)
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

        proj = self._projection.matrix

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
        self.drawable.shader.set_uniform("u_player_pos", self.agents["player"].sposition)
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

        # waypoints debugger
        if self.edit_mode:
            self.agents.path_debug_renderer.render(self._projection)

        #glDepthMask(False)
        self.agents.render(self._projection)

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
        self._projection._rotation[0] -= scroll_y / 30.

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self._projection._rotation[1] += dx / 30.

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
            ihit = tuple(int(x) for x in pos)
            self.agents.set_goal("player", ihit)

            if 0:  # editor
                block = self.chunk.block(*ihit)
                #print(hit, t, ihit, block.texture)
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
        if text in self._projection.PROJECTIONS:
            self._projection.init(text)
        if text == "f":
            self.set_fullscreen(not self.fullscreen)
        if text == "+":
            self._projection.zoom += 1.
        if text == "-":
            self._projection.zoom -= 1.
        if text == "d":
            self.debug_view = (self.debug_view + 1) % 2

    def get_ray(self, x, y):
        return self._projection.screen_to_ray(x, y)

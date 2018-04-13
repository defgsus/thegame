import time
import pyglet
import glm
import math
from pyglet.gl import *
from lib.opengl import *
from lib.geom import *
from lib.world import *
from lib.world.ChunkRenderer_shader import vert_src, frag_src
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
        self.texture = None
        self.mesh = self.chunk.create_mesh()
        self.drawable = self.mesh.create_drawable()
        self.drawable.shader.set_vertex_source(vert_src)
        self.drawable.shader.set_fragment_source(frag_src)

        self.texture2 = Texture2D()

        # edit mesh
        self.edit_drawable = Drawable()
        self.cur_edit_voxel = (-1,-1,-1)

        # waypoints test
        self.waypoints = self.chunk.create_waypoints()
        self.waypoints_mesh = self.waypoints.create_mesh(color=(.3,.3,.3))
        self.waypoints_drawable = Drawable()
        self.waypoint1 = None
        self.waypoint2 = None
        self.path = None
        self.path_changed = False
        self.path_drawable = Drawable()

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
        self.agents.create_agent("other", "./assets/pokeson2.png")
        self.agents["other"].set_position(glm.vec3(10, 15, 10) + .5)

        # projection
        self.projection = WorldProjection(self.width, self.height, WorldProjection.P_ISOMETRIC)
        self.projection.update(.4)

        # time(r)
        self.start_time = time.time()
        pyglet.clock.schedule_interval(self.update, 1.0 / 60.0)
        pyglet.clock.set_fps_limit(60)

    def update(self, dt):
        self.check_keys(dt)

        self.agents.update(dt)

        self.projection.width = self.width
        self.projection.height = self.height
        self.projection.user_transformation = glm.translate(glm.mat4(1), -self.agents["player"].sposition)
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
                if self.projection.projection == self.projection.P_ISOMETRIC:
                    dir = glm.vec3(glm.rotate(glm.mat4(1), -glm.pi()/4., (0,0,1)) * glm.vec4(dir, 0))
                dir *= min(1, dt*10.)
                self.agents["player"].move(dir)

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
            if not self.waypoints_mesh.is_empty():
                print("waypoint mesh", len(self.waypoints_mesh.lines_array()))
                self.waypoints_mesh.update_drawable(self.waypoints_drawable)
                self.waypoints_mesh.clear()

            if not self.waypoints_drawable.is_empty():
                mat = glm.translate(proj, (.5,.5,.2))
                self.waypoints_drawable.shader.set_uniform("u_projection", mat)
                self.waypoints_drawable.draw()

            if self.path_changed:
                if self.path:
                    mesh = LineMesh()
                    prev_node = None
                    for node in self.path:
                        if prev_node is not None:
                            mesh.add_line(self.waypoints.id_to_pos[prev_node], self.waypoints.id_to_pos[node])
                        prev_node = node
                    mesh.update_drawable(self.path_drawable)
                else:
                    self.path_drawable.clear()

            if not self.path_drawable.is_empty():
                mat = glm.translate(proj, (.6,.6,.4))
                self.path_drawable.shader.set_uniform("u_projection", mat)
                self.path_drawable.draw()

        glDisable(GL_DEPTH_TEST)
        self.agents.render(self.projection)

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
            ihit = tuple(int(x) for x in pos)
            block = self.chunk.block(*ihit)
            #print(hit, t, ihit, block.texture)
            if 0:
                block.space_type = 1
                block.texture = 40
                self.chunk_changed = True

            if not self.edit_mode:

                self.agents.set_goal("player", ihit)

            if self.edit_mode:
                node = self.waypoints.closest_node((ihit[0], ihit[1], 1))
                if self.waypoint1 is None:
                    self.waypoint1 = node
                else:
                    if self.waypoint2 is None:
                        self.waypoint2 = node
                    else:
                        d1 = glm.distance(ihit, self.waypoints.id_to_pos[self.waypoint1])
                        d2 = glm.distance(ihit, self.waypoints.id_to_pos[self.waypoint2])
                        if d1 < d2:
                            self.waypoint1 = node
                        else:
                            self.waypoint2 = node

                if self.waypoint1 is not None and self.waypoint2 is not None:
                    pathfinder = AStar(self.waypoints)
                    tstart = time.time()
                    self.path = pathfinder.search(self.waypoint1, self.waypoint2)
                    tend = time.time()
                    self.path_changed = True
                    print("path took %ss (%s fps)" % (tend-tstart, round(1./(tend-tstart), 2)))

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

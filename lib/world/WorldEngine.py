import glm

from lib.ai import *
from .WorldChunk import WorldChunk
from .Tileset import Tileset
from .WorldProjection import WorldProjection
from .render.ChunkRenderer import ChunkRenderer
from lib.opengl.RenderSettings import RenderSettings


class WorldEngine:

    def __init__(self):
        self.edit_mode = False
        self.click_voxel = (30,10,10)
        self.debug_view = 0

        self.renderer = None
        self.projection = WorldProjection(480, 320, projection=WorldProjection.P_ISOMETRIC)
        self.render_settings = RenderSettings(480, 320, projection=self.projection)

        # chunk
        self.tileset = Tileset.from_image(16, 16, "./assets/tileset02.png")
        self.chunk = WorldChunk(self.tileset)

        if 0:
            #self.chunk.from_heightmap(gen_heightmap())
            self.chunk.from_heightmap(HEIGHTMAP, do_flip_y=True)
        else:
            self.chunk.from_tiled("./assets/tiled/level03.json")

        # player
        self.agents = Agents(self.chunk)
        self.agents.create_agent("player", "./assets/pokeson.png")
        self.agents["player"].set_position(glm.vec3(14, 14, 10) + .5)

        # other guy
        follow = "player"
        for i in range(5):
            name = "other%s" % i
            self.agents.create_agent(name, "./assets/pokeson2.png")
            self.agents[name].set_position(glm.vec3(10, 15, 10) + .5)
            self.agents.set_follow(name, follow)
            follow = name

    def update(self, dt):
        self.agents.update(dt)

        self.projection.user_transformation = glm.translate(glm.mat4(1), -self.agents["player"].sposition)
        self.projection.update(dt)

    def render(self, time):
        self.render_settings.time = time

        if self.renderer is None:
            self.renderer = ChunkRenderer(self)

        self.renderer.render()

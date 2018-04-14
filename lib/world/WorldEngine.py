import glm

from lib.ai import *
from .WorldChunk import WorldChunk
from .Tileset import Tileset
from .WorldProjection import WorldProjection
from .ChunkRenderer import ChunkRenderer


class WorldEngine:

    def __init__(self, screen_width, screen_height):
        self.edit_mode = False
        self.click_voxel = (0,0,0)
        self.debug_view = 0

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.renderer = None

        # projection
        self.projection = WorldProjection(self.screen_width, self.screen_height, WorldProjection.P_ISOMETRIC)
        self.projection.update(.4)

        # chunk
        self.tileset = Tileset.from_image(16, 16, "./assets/tileset02.png")
        self.chunk = WorldChunk(self.tileset)

        if 0:
            #self.chunk.from_heightmap(gen_heightmap())
            self.chunk.from_heightmap(HEIGHTMAP, do_flip_y=True)
        else:
            self.chunk.from_tiled("./assets/tiled/level01.json")

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

    def update(self, dt):
        self.agents.update(dt)

        self.projection.user_transformation = glm.translate(glm.mat4(1), -self.agents["player"].sposition)
        self.projection.update(dt)

    def render(self, width, height, time):
        self.projection.width = width
        self.projection.height = height

        if self.renderer is None:
            self.renderer = ChunkRenderer(self)
        self.renderer.render(self.projection, time)

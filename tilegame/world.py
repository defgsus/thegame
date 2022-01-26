import math

import glm
import pyglet
import pybullet
import pybullet_data

from .map.tilemap import TilemapSampler
from . import objects


class World:

    def __init__(self):
        self.tile_map = TilemapSampler()
        self.player = objects.WalkerObject("player",)
        self.physics_client_id = pybullet.connect(pybullet.DIRECT)
        self.init_physics()
        self.object_map = dict()
        self.add_object(self.player)
        self.add_object(objects.Plane("plane"))
        self.add_object(objects.Sphere("sphere", location=glm.vec3(4, 2, 3.)))

    def __del__(self):
        pybullet.disconnect(physicsClientId=self.physics_client_id)

    def init_physics(self):
        pybullet.setAdditionalSearchPath(pybullet_data.getDataPath(), physicsClientId=self.physics_client_id)
        pybullet.setGravity(0, 0, -10, physicsClientId=self.physics_client_id)
        pybullet.setRealTimeSimulation(False, physicsClientId=self.physics_client_id)
        pybullet.setTimeStep(1. / 60., physicsClientId=self.physics_client_id)

    def add_object(self, obj: objects.ObjectBase):
        if obj.id in self.object_map:
            raise ValueError(f"Object id '{obj.id}' already used")
        self.object_map[obj.id] = obj
        obj.create_bullet_body()

    def update(self, time: float, dt: float):
        self.player.update(time, dt)
        pybullet.stepSimulation(physicsClientId=self.physics_client_id)
        # print(self.player.location)
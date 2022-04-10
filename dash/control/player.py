import math
from typing import Tuple, Optional

import pyglet
import pymunk
from pymunk import Vec2d, ShapeFilter

from .base import ControllerBase
from ..map import Object


class PlayerBugController(ControllerBase):

    class Foot:
        def __init__(
                self,
                controller: "PlayerBugController",
                anchor_pos: Vec2d, relative_pos: Vec2d, foot: Object, radius: float
        ):
            self.controller = controller
            self.anchor_pos = anchor_pos
            self.relative_pos = relative_pos
            self.object = foot
            self.radius = radius
            self.leg_joint = None
            self.world_joint = None

        def normal(self) -> Vec2d:
            """
            Current world normal (body -> foot)
            """
            return (self.object.position - self.controller.object.position).normalized()

        def contact_normal(self) -> Vec2d:
            """
            normal of world coordinates b minus a.

            Only call when `world_joint` is not None
            """
            delta: Vec2d = (
                self.world_joint.b.local_to_world(self.world_joint.anchor_b)
                - self.world_joint.a.local_to_world(self.world_joint.anchor_a)
            )
            return delta.normalized()

    def __init__(self, objects, pos: Tuple[float, float]):
        from ..map import Objects
        super().__init__()

        objects: Objects
        self.all_objects = objects
        self.move_normal: Optional[Vec2d] = None
        self.feet_rotation_movement = 0
        radius = .23
        small_radius = .1

        self.object = objects.add_object(
            shape_type="circle",
            pos=pos,
            mass=6.6,
            scale=radius*2.,
        )
        self.object.shape.filter = pymunk.ShapeFilter(categories=0b1)
        self.add_object(self.object)
        self.object.controller = self
        objects.add_controller(self)

        self.feet = []
        for i in range(12):
            r = i / 6 * math.pi

            anchor_pos = pymunk.Vec2d(
                (radius) * math.sin(r),
                (radius) * math.cos(r),
            )
            foot_rel_pos = pymunk.Vec2d(
                (radius + .1*small_radius) * math.sin(r),
                (radius + .1*small_radius) * math.cos(r),
            )

            foot_object = objects.add_object(
                shape_type="circle",
                pos=foot_rel_pos + pos,
                scale=small_radius * 2,
                mass=.1,
            )
            # foot_object.shape.friction = 10.
            foot_object.shape.filter = pymunk.ShapeFilter(categories=0b1)
            foot = self.Foot(self, anchor_pos, foot_rel_pos, foot_object, radius)
            self.feet.append(foot)

            foot.leg_joint = pymunk.PinJoint(
                self.object.body,   foot.object.body,
                anchor_pos,         (0, 0),
                #min=0, max=small_radius,
            )
            self.space.add(foot.leg_joint)

    def check_keys_2(self, keys: dict, dt: float):
        angular_velocity = 0.0
        self.move_normal = None
        if keys.get(pyglet.window.key.LEFT):
            angular_velocity += dt*100.
            self.move_normal = Vec2d(-1, 0)
            self.feet_rotation_movement -= dt
        if keys.get(pyglet.window.key.RIGHT):
            angular_velocity -= dt*100.
            self.move_normal = Vec2d(1, 0)
            self.feet_rotation_movement += dt

        if angular_velocity:
            self.object.body.angular_velocity += angular_velocity
            for foot in self.feet:
                foot.object.body.angular_velocity += angular_velocity

        if keys.get(pyglet.window.key.SPACE):
            self.jump()

    def check_keys(self, keys: dict, dt: float):
        self.move_normal = None
        dir_mapping = {
            pyglet.window.key.UP: (0, 1),
            pyglet.window.key.DOWN: (0, -1),
            pyglet.window.key.LEFT: (-1, 0),
            pyglet.window.key.RIGHT: (1, 0),
        }
        move_normal = Vec2d(0, 0)
        for key, delta in dir_mapping.items():
            if keys.get(key):
                move_normal += delta
                self.object.apply_impulse(Vec2d(*delta) * dt * 100)

        length = move_normal.length
        if length:
            self.move_normal = move_normal / length

        if keys.get(pyglet.window.key.SPACE):
            self.jump()

    def jump(self):
        for foot in self.feet:
            if foot.world_joint:
                self.object.apply_impulse(-foot.contact_normal() * 20.)
                self.space.remove(foot.world_joint)
                foot.world_joint = None
                foot.object.color = (1, 1, 1, 1)

    def update(self, time: float, dt: float):

        if self.move_normal is not None:
            for i, foot in enumerate(self.feet):
                #want_contact = .0 < math.sin(self.feet_rotation_movement * 10. + i / len(self.feet) * math.pi * 2)
                want_contact = .0 < foot.normal().dot(self.move_normal)

                if want_contact and not foot.world_joint:
                    #foot_world_pos = self.object.position + foot.relative_pos.rotated(self.object.rotation)
                    foot_world_pos = foot.object.position

                    info = self.space.point_query_nearest(
                        point=foot_world_pos + .1 * self.move_normal,
                        max_distance=foot.radius*1.3,
                        shape_filter=ShapeFilter(mask=ShapeFilter.ALL_MASKS() ^ 0b1),
                    )
                    if info:
                        # print("connect", foot.object, info.point, info.shape)
                        foot.world_joint = pymunk.DampedSpring(
                            a=foot.object.body,
                            b=info.shape.body,
                            anchor_a=(0, 0),
                            anchor_b=info.shape.body.world_to_local(info.point),
                            rest_length=0,#foot.radius,
                            stiffness=10000,
                            damping=10,
                        )
                        self.space.add(foot.world_joint)
                        foot.object.color = (1, 2, 1, 1)

                if not want_contact and foot.world_joint:
                    # print("disconnect", foot.object)
                    self.space.remove(foot.world_joint)
                    foot.world_joint = None
                    foot.object.color = (1, 1, 1, 1)
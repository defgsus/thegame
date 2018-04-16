import glm
from lib.world.render.AgentRenderer import AgentRenderer


class Agent:

    def __init__(self, chunk, renderer=None):
        self.name = ""
        self.chunk = chunk
        self.position = glm.vec3(0,0,0)
        self.velocity = glm.vec3(0)
        self.sposition = glm.vec3(self.position)
        self.renderer = renderer if renderer is not None else AgentRenderer()

        self.anim_stage = 0.
        self.direction = renderer.DOWN

    def set_position(self, pos):
        self.position = glm.vec3(pos)
        self.sposition = glm.vec3(pos)

    def jump(self, amt=1):
        if self.chunk.is_wall(int(self.sposition.x), int(self.sposition.y), int(self.sposition.z-.5), self.chunk.TOP):
            self.velocity += (0, 0, amt)

    def move(self, dir):
        self.position = self.sposition + dir
        #if self.chunk.block(int(newpos.x), int(newpos.y), int(newpos.z)).space_type == 0:
        #    self.position = newpos
        #newpos = self.position + glm.vec3(0,0,-.1)
        #if self.chunk.block(int(newpos.x), int(newpos.y), int(newpos.z)).space_type == 0:
        #    self.position = newpos
        #self.position.z -= self.velocity.z

        adir = glm.abs(dir)
        if adir.z > adir.x and adir.z > adir.y:
            return

        if adir.x > adir.y:
            self.direction = self.renderer.RIGHT if dir.x > 0 else self.renderer.LEFT
        else:
            self.direction = self.renderer.UP if dir.y > 0 else self.renderer.DOWN

    def update(self, dt):
        d = min(1, dt*5)

        # gravity
        if 1:
            newpos = self.position + d * glm.vec3(0,0,-3)
            if int(newpos.z) >= 1:
                if self.chunk.block(int(newpos.x), int(newpos.y), int(newpos.z)).space_type == 0:
                    self.position = newpos
        else:
            t, hit = self.chunk.cast_voxel_ray(self.position+(0,0,0), (0,0,-1))
            if hit:
                self.position.z -= t
                self.sposition.z -= t

        # advance spos to pos
        move = (self.position - self.sposition) + self.velocity
        if 0:
            newpos = self.sposition + d * move
            if self.chunk.block(int(newpos.x), int(newpos.y), int(newpos.z)).space_type == 0:
                self.sposition = newpos
        else:
            nextpos = glm.vec3(self.sposition)
            for i, ax in enumerate(((1,0,0), (0,1,0), (0,0,1))):
                newpos = self.sposition + d * move * ax
                if self.chunk.block(int(newpos.x-.2), int(newpos.y-.2), int(newpos.z)).space_type == 0\
                    and self.chunk.block(int(newpos.x+.2), int(newpos.y-.2), int(newpos.z)).space_type == 0\
                    and self.chunk.block(int(newpos.x-.2), int(newpos.y+.2), int(newpos.z)).space_type == 0\
                    and self.chunk.block(int(newpos.x+.2), int(newpos.y+.2), int(newpos.z)).space_type == 0:
                    nextpos[i] = newpos[i]
            self.sposition = nextpos

        self.velocity -= self.velocity * d * .5

        amt = glm.dot(move, move)
        if amt > .1:
            self.anim_stage += dt * 7.
            if self.anim_stage > 3.:
                self.anim_stage = 1.
        else:
            self.anim_stage = 0.

    def render(self, projection):
        self.renderer.render(projection, self.sposition, self.direction, int(self.anim_stage))
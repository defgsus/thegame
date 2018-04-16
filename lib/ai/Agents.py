import glm

from .Agent import Agent
from lib.world.render.AgentRenderer import AgentRenderer
from lib.opengl import Drawable
from lib.geom import LineMesh
from lib.ai.AStar import AStar


class Agents:

    def __init__(self, chunk):
        self.chunk = chunk
        self._agents = dict()
        self._pathfinder = AStar(self.chunk.waypoints)
        self._paths = dict()
        self._follower = dict()
        self._path_debug_renderer = None

    def __getitem__(self, name):
        return self._agents[name]

    def add_agent(self, name, agent):
        agent.chunk = self.chunk
        agent.name = name
        self._agents[name] = agent

    def create_agent(self, name, tileset_filename=None):
        agent = Agent(self.chunk, renderer=AgentRenderer(filename=tileset_filename))
        self.add_agent(name, agent)

    def release(self):
        for a in self._agents.values():
            a.release()
        if self._path_debug_renderer:
            self._path_debug_renderer.release()

    def render(self, projection):
        for agent in self._agents.values():
            agent.render(projection)

    def update(self, dt):
        import random
        # follow each other
        for fname in self._follower:
            goal = self._follower[fname]
            if goal[1] <= 0.:
                pos = glm.vec3(self[goal[0]].sposition)
                pos.x += random.uniform(1, 3) * (random.randrange(2)*2-1)
                pos.y += random.uniform(1, 3) * (random.randrange(2)*2-1)
                self.set_goal(fname, pos)
                goal[1] = random.uniform(1, 4)
            else:
                goal[1] -= dt

        # advance and finish paths
        del_path = []
        for name in self._paths:
            path = self._paths[name]
            if not path.finished():
                path.update(dt)
            else:
                del_path.append(name)
        for n in del_path:
            del self._paths[n]

        # advance agents
        for agent in self._agents.values():
            agent.update(dt)

    def get_closest_waypoint(self, name):
        pos = tuple(int(p) for p in self._agents[name].sposition)
        return self.chunk.waypoints.closest_node(pos)

    def set_follow(self, follower_name, goal_name=None):
        if not goal_name:
            if follower_name in self._follower:
                del self._follower[follower_name]
            return
        self._follower[follower_name] = [goal_name, 0.]

    def set_goal(self, name, pos):
        pos = tuple(int(p) for p in pos)

        from_node = self.get_closest_waypoint(name)
        to_node = self.chunk.waypoints.closest_node(pos)
        path = self._pathfinder.search(from_node, to_node)
        if path is None:
            print("'%s' unable to go to goal %s" % (name, pos))
            return
        if len(path) > 1:
            self._paths[name] = AgentPath(self, name, path)
            if self._path_debug_renderer:
                self._path_debug_renderer.path_changed = True

    @property
    def path_debug_renderer(self):
        if self._path_debug_renderer is None:
            self._path_debug_renderer = AgentsPathDebugRenderer(self)
        return self._path_debug_renderer


class AgentPath:
    """Temp structure to store and advance a path for an agent"""

    def __init__(self, agents, name, path):
        assert len(path) > 1
        self.agents = agents
        self.waypoints = self.agents.chunk.waypoints
        self.name = name
        self.path = path
        self.agent = self.agents[self.name]
        self.goal_pos = self.waypoints.id_to_pos[self.path[-1]]
        self.cur_index = 0
        self.min_dist = 0.2

    def finished(self):
        if self.cur_index >= len(self.path):
            return True
        return glm.distance(self.agent.sposition, self.goal_pos) <= self.min_dist

    def pos_at(self, index):
        node = self.path[int(index)]
        return self.waypoints.id_to_pos[node]

    def dir_at(self, index):
        i = int(index)
        i1 = i+1
        if i1 >= len(self.path):
            i, i1 = i-1, i1-1
        return glm.normalize(self.pos_at(i1) - self.pos_at(i))

    def update(self, dt):
        if self.cur_index+1 >= len(self.path):
            return False

        this_pos = self.waypoints.id_to_pos[self.path[self.cur_index]] + glm.vec3(.5,.5,0)
        next_node = self.path[self.cur_index+1]
        next_pos = self.waypoints.id_to_pos[next_node] + glm.vec3(.5,.5,0)
        #print(self.path, self.cur_index, next_node, self.agent.sposition, next_pos)

        dist = glm.distance(self.agent.sposition, next_pos)
        dir = (next_pos - self.agent.sposition) / dist

        self.agent.move(dir)
        #if self.agent.name == "player":
        #    print(this_pos.y, next_pos.y, self.agent.sposition.y)
        if next_pos.z > this_pos.z + .3 and next_pos.z > self.agent.sposition.z:
            self.agent.jump()

        if dist <= self.min_dist:
            self.cur_index += 1


class AgentsPathDebugRenderer:
    def __init__(self, agents):

        self.agents = agents
        self.waypoints = agents.chunk.waypoints
        self.waypoints_mesh = self.waypoints.create_mesh(color=(.3,.5,.5))
        self.waypoints_drawable = Drawable()
        self.waypoint1 = None
        self.waypoint2 = None
        self.path_changed = False
        self.path_drawable = Drawable()

    def release(self):
        self.waypoints_drawable.release()
        self.path_drawable.release()

    def render(self, projection):
        proj = projection.matrix

        if not self.waypoints_mesh.is_empty():
            print("waypoint mesh", len(self.waypoints_mesh.lines_array()))
            self.waypoints_mesh.update_drawable(self.waypoints_drawable)
            self.waypoints_mesh.clear()

        if not self.waypoints_drawable.is_empty():
            mat = glm.translate(proj, (.5,.5,.2))
            self.waypoints_drawable.shader.set_uniform("u_projection", mat)
            self.waypoints_drawable.draw()

        if self.path_changed:
            if self.agents._paths:
                mesh = LineMesh()
                for path in self.agents._paths.values():
                    prev_node = None
                    for node in path.path:
                        if prev_node is not None:
                            mesh.add_line(
                                self.waypoints.id_to_pos[prev_node],
                                self.waypoints.id_to_pos[node]
                            )
                        prev_node = node
                mesh.update_drawable(self.path_drawable)
            else:
                self.path_drawable.clear()

        if not self.path_drawable.is_empty():
            mat = glm.translate(proj, (.49, .49, .21))
            self.path_drawable.shader.set_uniform("u_projection", mat)
            self.path_drawable.draw()

import glm

from .Agent import Agent
from .AgentRenderer import AgentRenderer
from ..ai import AStar



class Agents:

    def __init__(self, chunk):
        self.chunk = chunk
        self._agents = dict()
        self._pathfinder = AStar(self.chunk.waypoints)
        self._paths = dict()
        self._follower = dict()

    def __getitem__(self, name):
        return self._agents[name]

    def add_agent(self, name, agent):
        agent.chunk = self.chunk
        self._agents[name] = agent

    def create_agent(self, name, tileset_filename=None):
        agent = Agent(self.chunk, renderer=AgentRenderer(filename=tileset_filename))
        self.add_agent(name, agent)

    def release(self):
        for a in self._agents.values():
            a.release()

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
        return glm.normalize(self.pos_at(i1) - glm.normalize(self.pos_at(i)))

    def update(self, dt):
        if self.cur_index+1 >= len(self.path):
            return False

        next_node = self.path[self.cur_index+1]
        next_pos = self.waypoints.id_to_pos[next_node] + glm.vec3(.5,.5,0)
        #print(self.path, self.cur_index, next_node, self.agent.sposition, next_pos)

        dist = glm.distance(self.agent.sposition, next_pos)
        dir = (next_pos - self.agent.sposition) / dist

        self.agent.move(dir)

        if dist <= self.min_dist:
            self.cur_index += 1

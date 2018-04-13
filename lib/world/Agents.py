import glm

from .Agent import Agent
from .AgentRenderer import AgentRenderer
from ..ai import AStar


class AgentPath:

    def __init__(self, agents, name, path):
        assert len(path) > 1
        self.agents = agents
        self.waypoints = self.agents.chunk.waypoints
        self.name = name
        self.path = path
        self.agent = self.agents[self.name]
        self.cur_index = 0

    def finished(self):
        return self.cur_index >= len(self.path)

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
        next_pos = self.waypoints.id_to_pos[next_node]

        dt = min(1, dt*5)
        dir = glm.normalize(next_pos - self.agent.sposition)
        self.agent.move(dir * dt)

        if glm.distance(self.agent.sposition, next_pos) < .1:
            self.cur_index += 1


class Agents:

    def __init__(self, chunk):
        self.chunk = chunk
        self._agents = dict()
        self._pathfinder = AStar(self.chunk.waypoints)
        self._paths = dict()

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
        for path in self._paths.values():
            if not path.finished():
                path.update(dt)

        for agent in self._agents.values():
            agent.update(dt)

    def get_closest_waypoint(self, name):
        pos = tuple(int(p) for p in self._agents[name].sposition)
        return self.chunk.waypoints.closest_node(pos)

    def set_goal(self, name, pos):
        pos = tuple(int(p) for p in pos)

        from_node = self.get_closest_waypoint(name)
        to_node = self.chunk.waypoints.closest_node(pos)
        path = self._pathfinder.search(from_node, to_node)
        if path is None:
            print("'%s' unable to go to goal" % name)
            return

        self._paths[name] = AgentPath(self, name, path)

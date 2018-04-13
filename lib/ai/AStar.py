import math
import glm


class AStar:

    def __init__(self, waypoints):
        self.nodes = waypoints

    def heuristic_goal_cost(self, n1, n2):
        if n1 == n2:
            return 0
        d = self.nodes.distance(n1, n2)
        return d
        #return pow(d, .001)  # prefer diagonals
        #return d * (1.1+math.sin(n1))
        #return 1. / (.01+d)

    def heuristic_step_cost(self, n1, n2, goal):
        if n1 == n2:
            return 0
        d = self.nodes.distance(n1, n2)
        if 0:  # avoid towards goal
            dir1 = self.nodes.direction(n1, n2)
            dir2 = self.nodes.direction(n1, goal)
            return glm.dot(dir1, dir2) * d
        return d

    def search(self, start_node, end_node):
        infinity = 2 << 31

        closed_set = set()
        open_set = {start_node}

        # cost of getting from start to this node
        g_score = {start_node: 0}

        # total cost if getting from start to end, through this node
        f_score = {end_node: self.heuristic_goal_cost(start_node, end_node)}

        came_from = dict()

        while open_set:
            # pick smallest f from open_set
            current_node = None
            min_score = infinity
            for n in open_set:
                f = f_score.get(n, infinity)
                if f < min_score or current_node is None:
                    min_score, current_node = f, n
            open_set.remove(current_node)

            # found!
            if current_node == end_node:
                path = [current_node]
                while current_node in came_from:
                    current_node = came_from[current_node]
                    path.append(current_node)
                return list(reversed(path))

            # flag as evaluated
            closed_set.add(current_node)

            for neighbor_node in self.nodes.adjacent_nodes(current_node):

                if neighbor_node in closed_set:
                    continue

                if neighbor_node not in open_set:
                    open_set.add(neighbor_node)

                g = g_score.get(current_node) + self.heuristic_step_cost(current_node, neighbor_node, end_node)
                # prune this path
                if g >= g_score.get(neighbor_node, infinity):
                    continue

                # continue this path
                came_from[neighbor_node] = current_node
                g_score[neighbor_node] = g
                f_score[neighbor_node] = g + self.heuristic_goal_cost(neighbor_node, end_node)

        return None




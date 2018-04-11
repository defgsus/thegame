import math


class WayPoints:

    def __init__(self):
        self.id_to_pos = dict()
        self.pos_to_id = dict()
        self.edges = dict()
        self.distances = dict()

    @property
    def num_nodes(self):
        return len(self.id_to_pos)

    @property
    def num_edges(self):
        return len(self.edges) // 2

    def add_node_pos(self, pos):
        if pos in self.pos_to_id:
            return self.pos_to_id[pos]
        idx = len(self.id_to_pos)
        self.pos_to_id[pos] = idx
        self.id_to_pos[idx] = pos
        return idx

    def add_edge(self, i1, i2):
        if i1 == i2:
            raise ValueError("WayPoints.add_edge_idx() with equal indices")
        if i1 not in self.edges:
            self.edges[i1] = [i2]
        else:
            self.edges[i1].append(i2)
        if i2 not in self.edges:
            self.edges[i2] = [i1]
        else:
            self.edges[i2].append(i1)

    def add_edge_pos(self, p1, p2):
        i1 = self.add_node_pos(p1)
        i2 = self.add_node_pos(p2)
        self.add_edge(i1, i2)

    def distance(self, i1, i2):
        p1 = self.id_to_pos[i1]
        p2 = self.id_to_pos[i2]
        px, py, pz = p1[0]-p2[0], p1[1]-p2[1], p1[2]-p2[2]
        return math.sqrt(px*px+py*py+pz*pz)

    def closest_node(self, pos):
        if pos in self.pos_to_id:
            return self.pos_to_id[pos]
        n, md = None, 10000000
        for p in self.pos_to_id:
            d = abs(pos[0]-p[0])+abs(pos[1]-p[1])+abs(pos[2]-p[2])
            if d < md:
                n, md = self.pos_to_id[p], d
        return n

    def create_mesh(self, color=(1, 1, 1)):
        from ..geom import LineMesh
        mesh = LineMesh()
        mesh.set_color(*color)
        for e1 in self.edges:
            for e2 in self.edges[e1]:
                mesh.add_line(
                    self.id_to_pos[e1],
                    self.id_to_pos[e2],
                )
        return mesh

import math


class WayPoints:
    """An undirected graph"""

    def __init__(self):
        self.id_to_pos = dict()
        self.pos_to_id = dict()
        self._edge_fwd = dict()
        self._edge_back = dict()
        self.distances = dict()

    @property
    def num_nodes(self):
        return len(self.id_to_pos)

    @property
    def num_edges(self):
        return len(self._edge_fwd) // 2

    def _add_node_pos(self, pos):
        """adding a node without connection leads to undefined behaviour"""
        if pos in self.pos_to_id:
            return self.pos_to_id[pos]
        idx = len(self.id_to_pos)
        self.pos_to_id[pos] = idx
        self.id_to_pos[idx] = pos
        return idx

    def has_edge(self, i1, i2):
        if i1 in self._edge_fwd:
            return i2 in self._edge_fwd[i1]
        if i1 in self._edge_back:
            return i2 in self._edge_back[i1]
        return False

    def add_edge(self, i1, i2):
        if i1 == i2:
            raise ValueError("WayPoints.add_edge(%s, %s)" % (i1, i2))
        if self.has_edge(i1, i2):
            return
        if i1 not in self._edge_fwd:
            self._edge_fwd[i1] = {i2}
        else:
            self._edge_fwd[i1].add(i2)
        if i2 not in self._edge_back:
            self._edge_back[i2] = {i1}
        else:
            self._edge_back[i2].add(i1)

    def add_edge_pos(self, p1, p2):
        if p1 == p2:
            raise ValueError("WayPoint.add_edge_pos(%s, %s)" % (p1, p2))
        i1 = self._add_node_pos(p1)
        i2 = self._add_node_pos(p2)
        self.add_edge(i1, i2)

    def distance(self, i1, i2):
        p1 = self.id_to_pos[i1]
        p2 = self.id_to_pos[i2]
        px, py, pz = p1[0]-p2[0], p1[1]-p2[1], p1[2]-p2[2]
        return math.sqrt(px*px+py*py+pz*pz)

    def direction(self, i1, i2, normalized=True):
        p1 = self.id_to_pos[i1]
        p2 = self.id_to_pos[i2]
        px, py, pz = p1[0]-p2[0], p1[1]-p2[1], p1[2]-p2[2]
        if normalized:
            d = math.sqrt(px*px+py*py+pz*pz)
            px, py, pz = px/d, py/d, pz/d
        return px, py, pz

    def closest_node(self, pos):
        if pos in self.pos_to_id:
            return self.pos_to_id[pos]
        n, md = None, 10000000
        for p in self.pos_to_id:
            d = abs(pos[0]-p[0])+abs(pos[1]-p[1])+abs(pos[2]-p[2])
            if d < md:
                n, md = self.pos_to_id[p], d
        return n

    def adjacent_nodes(self, node):
        adj = set()
        if node in self._edge_fwd:
            adj |= self._edge_fwd[node]
        if node in self._edge_back:
            adj |= self._edge_back[node]
        return adj

    def create_mesh(self, color=(1, 1, 1)):
        from ..geom import LineMesh
        mesh = LineMesh()
        mesh.set_color(*color)
        for e1 in self._edge_fwd:
            for e2 in self._edge_fwd[e1]:
                mesh.add_line(
                    self.id_to_pos[e1],
                    self.id_to_pos[e2],
                )
        return mesh




class DirectedGraph:
    """Simple directed graph mapping from any -> any"""

    def __init__(self):
        self._nodes = set()
        self._outputs = dict()
        self._inputs = dict()

    @property
    def nodes(self):
        return self._nodes

    def inputs(self, n):
        return self._inputs.get(n, set())

    def outputs(self, n):
        return self._outputs.get(n, set())

    def has_inputs(self, n):
        return n in self._inputs and self._inputs[n]

    def has_outputs(self, n):
        return n in self._outputs and self._outputs[n]

    def copy(self):
        g = DirectedGraph()
        g._nodes = self._nodes.copy()
        g._outputs = {n: self._outputs[n].copy() for n in self._outputs}
        g._inputs = {n: self._inputs[n].copy() for n in self._inputs}
        return g

    def add_node(self, n):
        self._nodes.add(n)

    def add_edge(self, n1, n2):
        self._nodes.add(n1)
        self._nodes.add(n2)

        if n1 not in self._outputs:
            self._outputs[n1] = {n2}
        else:
            self._outputs[n1].add(n2)

        if n2 not in self._inputs:
            self._inputs[n2] = {n1}
        else:
            self._inputs[n2].add(n1)

    def remove_edge(self, n1, n2):
        if n1 in self._outputs:
            if n2 in self._outputs[n1]:
                self._outputs[n1].remove(n2)

        if n2 in self._inputs:
            if n1 in self._inputs[n2]:
                self._inputs[n2].remove(n1)

    def serialize(self):
        """Return a list of nodes, such that each node comes before it's output nodes"""
        graph = self.copy()

        # nodes with no inputs (temporary space)
        beginnings = set()

        # collect them
        for n in graph.nodes:
            if not graph.has_inputs(n):
                beginnings.add(n)

        if not beginnings:
            raise ValueError("No start nodes in DirectedGraph")

        linear = []

        while beginnings:
            # grab a node from work list
            n = beginnings.pop()
            # and add to output
            linear.append(n)

            # for each outgoing edge
            for nout in list(graph.outputs(n)):

                # remove this edge
                graph.remove_edge(n, nout)

                # if no other input node, move to beginnings
                if not graph.has_inputs(nout):
                    beginnings.add(nout)

        # see if deconstructed everything
        for n in graph.nodes:
            if graph.has_inputs(n):
                raise ValueError("Loop in DirectedGraph involving node '%s'" % n)

        return linear



if __name__ == "__main__":

    g = DirectedGraph()
    g.add_edge(1, 2)
    g.add_edge(1, 3)
    g.add_edge(2, 4)
    g.add_edge(3, 4)
    #g.add_edge(4, 5)
    g.add_edge(5, 1)
    g.add_edge(10, 5)
    print(g.serialize())

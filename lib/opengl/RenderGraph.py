from .core.base import *


class RenderGraph:
    """
    Defines a directed graph for rendering stages
    """

    def __init__(self):
        self.nodes = dict()
        self.edges = dict()
        self.inputs = dict()

    def create_pipeline(self):
        from .RenderPipeline import RenderPipeline
        return RenderPipeline(self)

    @staticmethod
    def to_name(node_or_name):
        from .RenderNode import RenderNode
        if isinstance(node_or_name, RenderNode):
            return node_or_name.name
        return node_or_name

    def to_node(self, node_or_name):
        from .RenderNode import RenderNode
        if isinstance(node_or_name, RenderNode):
            return node_or_name
        return self.nodes.get(node_or_name)

    def add_node(self, node):
        if node.name in self.nodes:
            raise ValueError("Multiple RenderGraph.add_node('%s')" % node.name)
        self.nodes[node.name] = node

    def connect(self, node_from, output, node_to, input=0):
        """Connect to existing nodes by name or instance"""
        node_from = self.to_name(node_from)
        node_to = self.to_name(node_to)
        assert node_from in self.nodes
        assert node_to in self.nodes
        # add edge
        if node_from not in self.edges:
            self.edges[node_from] = {node_to}
        else:
            self.edges[node_from].add(node_to)
        # add connection config
        if node_to not in self.inputs:
            self.inputs[node_to] = {input: (node_from, output)}
        else:
            if input in self.inputs[node_to]:
                raise ValueError("Multiple input '%s' to node '%s'" % (input, node_to))
            self.inputs[node_to][input] = (node_from, output)

    def output_nodes(self, node):
        node = self.to_name(node)
        if node in self.edges:
            return self.edges[node]
        return set()

    def input_nodes(self, node):
        node = self.to_name(node)
        if node not in self.inputs:
            return set()
        ret = set()
        for ins in self.inputs[node].values():
            ret.add(ins[0])
        return ret


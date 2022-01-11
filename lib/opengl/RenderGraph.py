from typing import Union, Set

from .core.base import *
from ..graph.DirectedGraph import DirectedGraph
from .RenderNode import RenderNode

NodeOrName = Union[RenderNode, str]


class RenderGraph:
    """
    Defines a directed graph for rendering stages
    """
    def __init__(self):
        self.graph = DirectedGraph()
        self.nodes = dict()
        self.inputs = dict()

    def create_pipeline(self):
        from .RenderPipeline import RenderPipeline
        return RenderPipeline(self)

    @staticmethod
    def to_name(node_or_name: NodeOrName) -> str:
        from .RenderNode import RenderNode
        if isinstance(node_or_name, RenderNode):
            return node_or_name.name
        return node_or_name

    def to_node(self, node_or_name: NodeOrName) -> RenderNode:
        if isinstance(node_or_name, RenderNode):
            return node_or_name
        return self.nodes.get(node_or_name)

    def add_node(self, node: RenderNode) -> RenderNode:
        if node.name in self.nodes:
            raise ValueError("Multiple RenderGraph.add_node('%s')" % node.name)
        if node.num_passes() > 1 and node.num_multi_sample() > 1:
            raise ValueError("Sorry, multi-pass with multi-sample is not allowed for RenderNode '%s'" % node.name)
        self.nodes[node.name] = node
        self.graph.add_node(node.name)
        return node

    def connect(
            self,
            node_from: NodeOrName,
            output: Union[str, int],
            node_to: NodeOrName,
            input: Union[str, int] = "0"
    ):
        """Connect to existing nodes by name or instance"""
        node_from = self.to_name(node_from)
        node_to = self.to_name(node_to)
        assert node_from in self.nodes
        assert node_to in self.nodes
        assert output in self.to_node(node_from).output_slots(), \
            f"output '{output}' not in {node_from} outputs {self.to_node(node_from).output_slots()}"
        # add edge
        self.graph.add_edge(node_from, node_to)
        # add connection config
        if node_to not in self.inputs:
            self.inputs[node_to] = {input: (node_from, output)}
        else:
            if input in self.inputs[node_to]:
                raise ValueError("Multiple input '%s' to node '%s'" % (input, node_to))
            self.inputs[node_to][input] = (node_from, output)

    def output_nodes(self, node: NodeOrName) -> Set[str]:
        return self.graph.outputs(self.to_name(node))

    def input_nodes(self, node: NodeOrName) -> Set[str]:
        return self.graph.inputs(self.to_name(node))


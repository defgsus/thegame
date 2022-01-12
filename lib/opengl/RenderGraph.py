from typing import Union, Set, Optional, Dict

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
        self.inputs: Dict[str, Dict] = dict()

    def create_pipeline(self):
        from .RenderPipeline import RenderPipeline
        return RenderPipeline(self)

    @staticmethod
    def to_name(node_or_name: NodeOrName) -> str:
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
            from_node: NodeOrName,
            from_slot: Union[str, int],
            to_node: NodeOrName,
            to_slot: Union[str, int] = 0,
            min_filter: Optional[int] = None,
            mag_filter: Optional[int] = None,
    ):
        """Connect to existing nodes by name or instance"""
        from_node = self.to_name(from_node)
        to_node = self.to_name(to_node)
        assert from_node in self.nodes
        assert to_node in self.nodes
        assert from_slot in self.to_node(from_node).output_slots(), \
            f"output '{from_slot}' not in {from_node} outputs {self.to_node(from_node).output_slots()}"

        # add edge
        self.graph.add_edge(from_node, to_node)

        # add connection config
        connection = {
            "from_node": from_node,
            "from_slot": from_slot,
            "to_slot": to_slot,
            "min_filter": min_filter,
            "mag_filter": mag_filter,
        }
        if to_node not in self.inputs:
            self.inputs[to_node] = {to_slot: connection}
        else:
            if to_slot in self.inputs[to_node]:
                raise ValueError("Multiple input to slot '%s' in node '%s'" % (to_slot, to_node))
            self.inputs[to_node][to_slot] = connection

    def output_nodes(self, node: NodeOrName) -> Set[str]:
        return self.graph.outputs(self.to_name(node))

    def input_nodes(self, node: NodeOrName) -> Set[str]:
        return self.graph.inputs(self.to_name(node))


from typing import List, Dict, Optional, Any, cast

import networkx as nx

from lineapy.data.types import (
    Node,
    NodeType,
    DirectedEdge,
    LineaID,
    ArgumentNode,
    VariableAliasNode,
)


class Graph(object):
    def __init__(self, nodes: List[Node], edges: Optional[List[DirectedEdge]] = None):
        """
        Note:
        - edges could be none for very simple programs
        """
        if edges is None:
            edges = []
        self._nodes: List[Node] = nodes
        self._ids: Dict[LineaID, Node] = dict((n.id, n) for n in nodes)
        self._edges: List[DirectedEdge] = edges
        self._graph = nx.DiGraph()
        self._graph.add_nodes_from([node.id for node in nodes])
        self._graph.add_edges_from(
            [(edge.source_node_id, edge.sink_node_id) for edge in edges]
        )

    @property
    def graph(self) -> nx.DiGraph:
        return self._graph

    @property
    def ids(self) -> Dict[LineaID, Node]:
        return self._ids

    def visit_order(self) -> List[LineaID]:
        return list(nx.topological_sort(self.graph))

    def get_parents(self, node: Node) -> List[Node]:
        return list(self.graph.predecessors(node))

    def get_ancestors(self, node: Node) -> List[Node]:
        return list(nx.ancestors(self.graph, node))

    def get_children(self, node: Node) -> List[Node]:
        return list(self.graph.successors(node))

    def get_descendants(self, node: Node) -> List[Node]:
        return list(nx.descendants(self.graph, node))

    def get_node(self, node_id: Optional[LineaID]) -> Optional[Node]:
        if node_id in self.ids:
            return self.ids[node_id]
        return None

    def get_node_value(self, node: Optional[Node]) -> Optional[Any]:
        if node is None:
            return None

        # find the original source node in a chain of aliases
        if node.node_type is NodeType.VariableAliasNode:
            node = cast(VariableAliasNode, node)
            source = self.get_node(node.source_variable_id)
            if source is None:
                print("WARNING: Could not find source node from id.")
                return None

            if source.node_type is NodeType.VariableAliasNode:
                source = cast(VariableAliasNode, source)

                while (
                    source is not None
                    and source.node_type is NodeType.VariableAliasNode
                ):
                    source = cast(VariableAliasNode, source)
                    source = self.get_node(source.source_variable_id)

            return source.value

        elif node.node_type is NodeType.ArgumentNode:
            node = cast(ArgumentNode, node)
            if node.value_literal is not None:
                return node.value_literal
            elif node.value_node_id is not None:
                return self.get_node_value(self.get_node(node.value_node_id))
            return None
        else:
            return node.value

    def get_node_value_from_id(self, node_id: Optional[LineaID]) -> Optional[Any]:
        node = self.get_node(node_id)
        return self.get_node_value(node)

    def print(self):
        for n in self._nodes:
            print(n)
        for e in self._edges:
            print(e)

    def __str__(self):
        self.print()

    def __repr__(self):
        self.print()

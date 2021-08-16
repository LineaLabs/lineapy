from typing import List, Dict, Optional

import networkx as nx

from lineapy.data.types import Node, NodeType, DirectedEdge, LineaID


class Graph(object):
    """
    TODO:
    - implement the getters by wrapping around networkx (see https://github.com/LineaLabs/backend-take-home/blob/main/dag.py for simple reference)
    """

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

    def get_node(self, node_id: LineaID) -> Node:
        if node_id in self.ids:
            return self.ids[node_id]
        return None

    def print(self):
        # TODO: improve printing (cc @dhruv)
        for n in self._nodes:
            print(n)
        for e in self._edges:
            print(e)

    def __str__(self):
        self.print()

    def __repr__(self):
        self.print()

from typing import Dict, Iterator, List, Optional

import networkx as nx

from lineapy.data.types import LineaID, Node, SessionContext
from lineapy.graph_reader.graph_printer import GraphPrinter
from lineapy.utils.analytics.event_schemas import CyclicGraphEvent
from lineapy.utils.analytics.usage_tracking import track
from lineapy.utils.utils import prettify


class Graph(object):
    def __init__(self, nodes: List[Node], session_context: SessionContext):
        """
        Graph is the core abstraction in LineaPy that is automatically generated
        by capturing and analyzing user code. Nodes in Graph correspond to
        variables and function calls from user code, and edges indicate
        dependencies. This is the common IR upon which all LineaPy applications,
        such as code cleanup and DAG generation, are built.

        :param nodes: a list of LineaPy Nodes that make up the graph.
        :param session_context: the session context associated with the graph

        NOTE: The information in session_context is semantically important to
        the notion of a Graph. Concretely, we are starting to also use the code
        entry from the session_context.
        """
        self.nodes: List[Node] = nodes
        self.ids: Dict[LineaID, Node] = dict((n.id, n) for n in nodes)
        self.nx_graph = nx.DiGraph()
        self.nx_graph.add_nodes_from([node.id for node in nodes])

        self.nx_graph.add_edges_from(
            [
                (parent_id, node.id)
                for node in nodes
                for parent_id in node.parents()
                if parent_id in set(self.ids.keys())
            ]
        )

        self.session_context = session_context

        # Checking whether the linea graph created is cyclic or not
        if not nx.is_directed_acyclic_graph(self.nx_graph):
            track(CyclicGraphEvent(""))

    def __eq__(self, other) -> bool:
        return nx.is_isomorphic(self.nx_graph, other.nx_graph)

    def print(self, **kwargs) -> str:
        return GraphPrinter(self, **kwargs).print()

    def get_parents(self, node_id: LineaID) -> List[LineaID]:
        return list(self.nx_graph.predecessors(node_id))

    def get_ancestors(self, node_id: LineaID) -> List[LineaID]:
        return list(nx.ancestors(self.nx_graph, node_id))

    def get_children(self, node_id: LineaID) -> List[LineaID]:
        return list(self.nx_graph.successors(node_id))

    def get_descendants(self, node_id: LineaID) -> List[LineaID]:
        return list(nx.descendants(self.nx_graph, node_id))

    def get_leaf_nodes(self) -> List[LineaID]:
        return [
            node
            for node in self.nx_graph.nodes
            if self.nx_graph.out_degree(node) == 0
        ]

    def get_node(self, node_id: Optional[LineaID]) -> Optional[Node]:
        if node_id is not None and node_id in self.ids:
            return self.ids[node_id]
        return None

    def get_subgraph(self, nodes: List[Node]) -> "Graph":
        """
        Get a subgraph of the current graph induced by the input nodes.

        :param nodes: The nodes in the subgraph
        :return: A new `Graph` that contains `nodes` and the edges between
        `nodes` in the current Graph and has the same session_context.
        """
        return Graph(nodes, self.session_context)

    def get_subgraph_from_id(self, nodeids: List[LineaID]) -> "Graph":
        """
        Get subgraph from list of LineaID
        """
        nodes: List[Node] = []
        for node_id in nodeids:
            node = self.get_node(node_id)
            if node is not None:
                nodes.append(node)
        return self.get_subgraph(nodes)

    def __str__(self):
        return prettify(
            self.print(
                include_source_location=False,
                include_id_field=True,
                include_session=False,
            )
        )

    def __repr__(self):
        return prettify(self.print())

    def visit_order(self) -> Iterator[Node]:
        return iter(self.nodes)

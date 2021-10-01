from queue import PriorityQueue, Queue
from typing import Iterator, TypeVar, cast, List, Dict, Optional, Any, Callable

import networkx as nx

from lineapy.graph_reader.graph_printer import GraphPrinter
from lineapy.data.types import (
    LineaID,
    Node,
    ArgumentNode,
    NodeValueType,
    NodeType,
    CallNode,
    SessionContext,
    VariableNode,
    DataSourceNode,
    ImportNode,
    DirectedEdge,
)
from lineapy.graph_reader.graph_util import (
    get_arg_position,
    get_edges_from_nodes,
    sort_node_by_position,
)
from lineapy.utils import (
    InternalLogicError,
    NullValueError,
    debug_log,
    listify,
)


class Graph(object):
    def __init__(self, nodes: List[Node], session_context: SessionContext):
        """
        Graph represents a
        It is constructed based on the following variables:
        :param nodes: a list of nodes and the session context in wh
        :param session_context: the session context associated with the graph

        NOTE:
        - It makes sense to include session_context in the constructor of
          the graph because the information in session_context is semantically
          important to the notion of a Graph. Concretely, we are starting
          to also use the code entry from the session_context.
        """
        self._nodes: List[Node] = nodes
        self._ids: Dict[LineaID, Node] = dict((n.id, n) for n in nodes)
        self._nx_graph = nx.DiGraph()
        self._nx_graph.add_nodes_from([node.id for node in nodes])

        self._edges: List[DirectedEdge] = list(get_edges_from_nodes(nodes))
        self._nx_graph.add_edges_from(
            [(edge.source_node_id, edge.sink_node_id) for edge in self._edges]
        )
        # FIXME this is kinda ugly
        self._nx_graph.add_edges_from(
            [
                (edge.source_node_id, edge.sink_node_id)
                for edge in self._get_edges_from_line_number()
            ]
        )
        self.session_context = session_context

        # validation
        if not nx.is_directed_acyclic_graph(self._nx_graph):
            raise InternalLogicError("Graph should not be cyclic")

    @property
    def nx_graph(self) -> nx.DiGraph:
        return self._nx_graph

    @property
    def ids(self) -> Dict[LineaID, Node]:
        return self._ids

    @property
    def nodes(self) -> List[Node]:
        return self._nodes

    @property
    def source_code(self) -> str:
        """
        Note that this is named "source_code" to emphasize that this was the
          original code, in the case where the graph is modified, the
          "derived_code" would be different
        """
        return self.session_context.code

    def __eq__(self, other) -> bool:
        return nx.is_isomorphic(self.nx_graph, other.nx_graph)

    def print(self, **kwargs) -> str:
        return GraphPrinter(self, **kwargs).print()

    @listify
    def visit_order(self) -> Iterator[Node]:
        """
        Just using the line number as tie breaker for now since we don't have
          a good way to track dependencies
          Note that we cannot just use the line number to sort because
            there are nodes created by us that do not have line numbers...
        """

        # Generally, we want to traverse the graph in a way to maintain two
        # constraints:

        # 1. All parents must be traveresed before their children
        # 2. If we have any freedom, those with earlier line number should come first

        # To do this, we do a breadth first traversal, keeping our queue ordered
        # by their line number. The sorting is done via the __lt__ method
        # of the Node
        queue = PriorityQueue[Node]()

        # We also keep a mapping of each node to the number of parents left
        # which have not been visited yet.
        remaining_parents = {
            node.id: self.nx_graph.in_degree(node.id) for node in self.nodes
        }
        # We also keep track of all nodes we have already added to the queue
        # so that we don't add them again
        seen = set[LineaID]()
        # First we add all of the nodes to the queue which have no parents
        for node in self.nodes:
            if self.nx_graph.in_degree(node.id) == 0:
                seen.add(node.id)
                queue.put(node)

        while queue.qsize():
            # Find the first node in the queue whcih has all its parents removed
            node = queue_get_when(
                queue, lambda n: remaining_parents[n.id] == 0
            )

            # Then, we add all of its children to the queue, making sure to mark
            # for each that we have seen one of its parents
            yield node
            for child_id in self.get_children(node):
                remaining_parents[child_id] -= 1
                if child_id in seen:
                    continue
                child_node = self.ids[child_id]
                queue.put(child_node)
                seen.add(child_id)

    def get_parents(self, node: Node) -> List[LineaID]:
        return list(self.nx_graph.predecessors(node.id))

    def get_ancestors(self, node_id: LineaID) -> List[LineaID]:
        return list(nx.ancestors(self.nx_graph, node_id))

    def get_children(self, node: Node) -> List[LineaID]:
        return list(self.nx_graph.successors(node.id))

    def get_descendants(self, node: Node) -> List[LineaID]:
        return list(nx.descendants(self.nx_graph, node.id))

    def get_leaf_nodes(self) -> List[LineaID]:
        return [
            node
            for node in self.nx_graph.nodes
            if self.nx_graph.out_degree(node) == 0
        ]

    def _get_edges_from_line_number(self) -> List[DirectedEdge]:
        edges = []
        # find all data source nodes
        for node in self.nodes:
            if node.node_type is NodeType.DataSourceNode:
                descendants = [
                    n
                    for n in self.get_descendants(node)
                    if n is not None
                    and self.get_node_else_raise(n).node_type
                    is NodeType.CallNode
                ]

                # sort data source nodes children
                # FIXME: lineno check
                descendants.sort(
                    key=lambda n: self.get_node_else_raise(n).lineno
                )
                # add edges between children
                for d in range(len(descendants) - 1):
                    if self.nx_graph.has_edge(
                        descendants[d], descendants[d + 1]
                    ) or self.nx_graph.has_edge(
                        descendants[d + 1], descendants[d]
                    ):
                        continue
                    edges.append(
                        DirectedEdge(
                            source_node_id=descendants[d],
                            sink_node_id=descendants[d + 1],
                        )
                    )
        # print(edges)
        return edges

    def get_node(self, node_id: Optional[LineaID]) -> Optional[Node]:
        if node_id is not None and node_id in self.ids:
            return self.ids[node_id]
        return None

    def get_node_else_raise(self, node_id: LineaID) -> Node:
        if node_id is None or node_id not in self.ids:
            raise NullValueError(f"Could not find {node_id}")
        return self.ids[node_id]

    def get_node_value(self, node: Optional[Node]) -> Optional[NodeValueType]:
        if node is None:
            return None

        # find the original source node in a chain of aliases
        if node.node_type is NodeType.VariableNode:
            node = cast(VariableNode, node)
            source = self.get_node(node.source_node_id)
            if source is None:
                print("WARNING: Could not find source node from id.")
                return None

            if source.node_type is NodeType.VariableNode:
                source = cast(VariableNode, source)

                while (
                    source is not None
                    and source.node_type is NodeType.VariableNode
                ):
                    source = cast(VariableNode, source)
                    source = self.get_node(source.source_node_id)

            return source.value  # type: ignore

        elif node.node_type is NodeType.ArgumentNode:
            node = cast(ArgumentNode, node)
            if node.value_literal is not None:
                return node.value_literal
            elif node.value_node_id is not None:
                return self.get_node_value(self.get_node(node.value_node_id))
            return None

        elif node.node_type is NodeType.DataSourceNode:
            node = cast(DataSourceNode, node)
            return node.access_path

        elif node.node_type is NodeType.ImportNode:
            node = cast(ImportNode, node)
            return node.module
        else:
            return node.value  # type: ignore

    def get_node_value_from_id(
        self, node_id: Optional[LineaID]
    ) -> Optional[Any]:
        node = self.get_node(node_id)
        return self.get_node_value(node)

    def get_arguments_from_call_node(
        self, node: CallNode
    ) -> tuple[List[NodeValueType], dict[str, NodeValueType]]:
        """
        FIXME: rather than using our loop comprehension, we should rely
          on database joins
        """
        arg_nodes = []
        kwarg_values = {}
        # Iterate through arguments and append to args/kwargs
        for arg in node.arguments:
            argument_node = cast(ArgumentNode, self.get_node_else_raise(arg))
            if argument_node.keyword is not None:
                kwarg_values[argument_node.keyword] = self.get_node_value(
                    argument_node
                )
            else:
                arg_nodes.append(argument_node)

        arg_nodes.sort(key=get_arg_position)

        return [self.get_node_value(a) for a in arg_nodes], kwarg_values

    def get_subgraph(self, nodes: List[Node]) -> "Graph":
        """
        FIXME
        """
        return Graph(nodes, self.session_context)

    def __str__(self):
        return self.print()

    def __repr__(self):
        return self.print()


T = TypeVar("T")


def queue_get_when(queue: Queue[T], filter_fn: Callable[[T], bool]) -> T:
    """
    Gets the first element in the queue that satisfies the filter function.
    """
    # We have to pop off a number of elements, stopping when we find one that
    # satisfies our conditional, since we can't iterate through a queue.
    popped_off = [queue.get()]
    while not filter_fn(popped_off[-1]):
        popped_off.append(queue.get())
    *add_back_to_queue, found = popped_off
    for tmp_node in add_back_to_queue:
        queue.put(tmp_node)
    return found

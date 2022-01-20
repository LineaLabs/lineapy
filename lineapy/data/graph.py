from queue import PriorityQueue, Queue
from typing import Callable, Dict, Iterator, List, Optional, Set, TypeVar

import networkx as nx

from lineapy.data.types import LineaID, Node, SessionContext
from lineapy.graph_reader.graph_printer import GraphPrinter
from lineapy.utils.utils import listify, prettify


class Graph(object):
    def __init__(self, nodes: List[Node], session_context: SessionContext):
        """
        Graph represents a
        It is constructed based on the following variables:
        :param nodes: a list of nodes and the session context in wh
        :param session_context: the session context associated with the graph

        NOTE:
        # TODO: Possibly remove session context since we aren't using it anywhere
        # we refer to the graph
        - It makes sense to include session_context in the constructor of
          the graph because the information in session_context is semantically
          important to the notion of a Graph. Concretely, we are starting
          to also use the code entry from the session_context.
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
            ]
        )

        self.session_context = session_context

        # validation
        if not nx.is_directed_acyclic_graph(self.nx_graph):
            raise AssertionError("Graph should not be cyclic")

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
        # TODO: See if we could replace this with python's built in topological sort
        # https://docs.python.org/3/library/graphlib.html
        # It seems to suggest that resulting order is determined by insertion order
        # so this could possibly also implicitly sort by line number, if we insert
        # in that order.

        # Generally, we want to traverse the graph in a way to maintain two
        # constraints:

        # 1. All parents must be traveresed before their children
        # 2. If we have any freedom, those with earlier line number should come first

        # To do this, we do a breadth first traversal, keeping our queue ordered
        # by their line number. The sorting is done via the __lt__ method
        # of the Node
        queue: PriorityQueue[Node] = PriorityQueue()

        # We also keep track of all nodes we have already added to the queue
        # so that we don't add them again
        seen: Set[LineaID] = set()

        # We also keep a mapping of each node to the number of parents left
        # which have not been visited yet.
        # Note that we want to skip counting parents which are not part of our nodes
        # This can happen we evaluate part of a graph, then another part.
        # When evaluating the next part, we just have those nodes, so some
        # of the parents will be missing, we assume they are already executed
        remaining_parents: Dict[str, int] = {}

        for node in self.nodes:
            n_remaining_parents = len(
                [
                    parent_id
                    for parent_id in self.nx_graph.pred[node.id]
                    if parent_id in self.ids
                ]
            )
            # First we add all of the nodes to the queue which have no parents

            if n_remaining_parents == 0:
                seen.add(node.id)
                queue.put(node)
            remaining_parents[node.id] = n_remaining_parents

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

    def get_node(self, node_id: Optional[LineaID]) -> Optional[Node]:
        if node_id is not None and node_id in self.ids:
            return self.ids[node_id]
        return None

    def get_subgraph(self, nodes: List[Node]) -> "Graph":
        """
        FIXME
        """
        return Graph(nodes, self.session_context)

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


T = TypeVar("T")


def queue_get_when(queue: "Queue[T]", filter_fn: Callable[[T], bool]) -> T:
    """
    Gets the first element in the queue that satisfies the filter function.
    """
    # We have to pop off a number of elements, stopping when we find one that
    # satisfies our conditional, since we can't iterate through a queue.

    # Use a timeout of 0 for the gets, otherewise if we have some bug
    # where we are trying to get off the queue and its empty it will just
    # block forever. with a timeout of 0, it will raise an exception instead.
    popped_off = [queue.get(timeout=0)]
    while not filter_fn(popped_off[-1]):
        popped_off.append(queue.get(timeout=0))
    *add_back_to_queue, found = popped_off
    for tmp_node in add_back_to_queue:
        queue.put(tmp_node)
    return found

from queue import PriorityQueue, Queue
from typing import Callable, Dict, Iterator, List, Optional, Set, TypeVar

import networkx as nx

from lineapy.data.types import IfNode, LineaID, Node, SessionContext
from lineapy.db.db import RelationalLineaDB
from lineapy.graph_reader.graph_printer import GraphPrinter
from lineapy.utils.analytics.event_schemas import CyclicGraphEvent
from lineapy.utils.analytics.usage_tracking import track
from lineapy.utils.utils import listify, prettify


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

    @listify
    def visit_order(self) -> Iterator[Node]:
        """
        Just using the line number as the tie-breaker for now since we don't
        have a good way to track dependencies.
        Note that we cannot just use the line number to sort because there are
        nodes created by us that do not have line numbers.
        """
        # TODO: Move this out of `Graph` and into classes that operate on top
        #  of the graph.

        # Before the introduction of Control Flow Analysis, the Linea Graph
        # could be represented as a Directed Acyclic Graph where each node could
        # be thought of as a computation with its parents as its dependencies.
        # This was possible as without control flow analysis, we were only
        # dealing with straight line code, which essentially is a sequence of
        # instructions executed one after another with no jumps.
        # However, with the introduction of control flow, we need to introduce
        # cycles in a graph to correspond to the cyclic dependencies possible,
        # especially in loops, as the only way to avoid cycles would be to
        # effectively unroll loops, which can become prohibitively expensive as
        # the number of iterations in a loop increases.

        # Cycles in the graph would be enough to represent data/control
        # dependencies, however while executing the graph we cannot depend on
        # future information to be present. We need a way to break cycles while
        # executing the graph, for which we currently resort to removing certain
        # edges in the graph, to ensure we are able to obtain a topological
        # ordering of the nodes, so that any node being executed depends on a
        # value which is already defined.

        # For a Directed Acyclic Graph, generally, we want to traverse the graph
        # in a way to maintain two constraints:

        # 1. All parents must be traversed before their children
        # 2. If permitted, nodes with smaller line numbers should come first

        # To do this, we do a breadth first traversal, keeping our queue ordered
        # by their line number. The sorting is done via the __lt__ method
        # of the Node
        queue: PriorityQueue[Node] = PriorityQueue()

        # We also keep track of all nodes we have already added to the queue
        # so that we don't add them again.
        seen: Set[LineaID] = set()

        # We also keep a mapping of each node to the number of parents left
        # which have not been visited yet.
        # Note that we want to skip counting parents which are not part of our
        # nodes. This can happen we evaluate part of a graph, then another part.
        # When evaluating the next part, we just have those nodes, so some
        # parents will be missing, we assume they are already executed.

        # We also want to remove certain nodes which result in a cycle. In case
        # a cycle is present, we would have a set of nodes, all of which have a
        # nonzero number of non-executed parents. To find the next node to
        # execute, we want one of the remaining nodes to have zero non-executed
        # parents, which indicates to us that the particular node can be
        # executed as all required information is present.

        # We have certain cases of removing parents in order to ensure no cycles
        # in the execution graph.
        remaining_parents: Dict[str, int] = {}

        for node in self.nodes:
            n_remaining_parents = len(
                [
                    parent_id
                    for parent_id in self.nx_graph.pred[node.id]
                    if parent_id in self.ids
                ]
            )

            # Removing certain edges to ensure the graph for execution is
            # acyclic, to generate a proper order for execution of nodes

            # Simply by reducing the counter `n_remaining_counter` by the
            # appropriate amount is sufficient as we check whether n_remaining_
            # parents for a particular node is zero for deciding whether it can
            # be executed next, rather than modifying the edges in the graph.

            # There is a cyclic dependency amongst and IfNode and ElseNode,
            # both being connected to each other. To break the cycle, we do not
            # consider the connection from the IfNode to the ElseNode (ElseNode
            # is not a dependency for IfNode to run)
            if isinstance(node, IfNode):
                if node.companion_id is not None:
                    n_remaining_parents -= 1

            # First we add all the nodes to the queue which have no parents.
            if n_remaining_parents == 0:
                seen.add(node.id)
                queue.put(node)
            remaining_parents[node.id] = n_remaining_parents

        while queue.qsize():
            # Find the first node in the queue which has all its parents removed
            node = queue_get_when(
                queue, lambda n: remaining_parents[n.id] == 0
            )

            # Then, we add all of its children to the queue, making sure to mark
            # for each that we have seen one of its parents
            yield node
            for child_id in self.get_children(node.id):
                remaining_parents[child_id] -= 1
                if child_id in seen:
                    continue
                child_node = self.ids[child_id]
                queue.put(child_node)
                seen.add(child_id)

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

    def get_subgraph_sink_source(
        self, sinks: List[LineaID], sources: List[LineaID]
    ) -> "Graph":

        temp_nx_graph = self.nx_graph.copy()

        for node in self.nodes:
            for parent_id in node.parents():
                if parent_id in sources:
                    temp_nx_graph.remove_edge(parent_id, node.id)

        subgraph_nodes = dict()

        for sink in sinks:
            subgraph_nodes.update({id: self.ids[sink]})
            subgraph_nodes.update(
                {id: self.ids[id] for id in nx.ancestors(temp_nx_graph, sink)}
            )

        return Graph(list(subgraph_nodes.values()), self.session_context)

    @classmethod
    def create_session_graph(cls, db: RelationalLineaDB, session_id: LineaID):
        session_context = db.get_session_context(session_id)
        session_nodes = db.get_nodes_for_session(session_id)
        return cls(session_nodes, session_context)

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

    # Use a timeout of 0 for the gets. Otherwise, if we have some bug
    # where we are trying to get off an empty queue, it will just
    # block forever. With a timeout of 0, it will raise an exception instead.
    popped_off = [queue.get(timeout=0)]
    while not filter_fn(popped_off[-1]):
        popped_off.append(queue.get(timeout=0))
    *add_back_to_queue, found = popped_off
    for tmp_node in add_back_to_queue:
        queue.put(tmp_node)
    return found

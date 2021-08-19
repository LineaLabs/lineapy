from lineapy.data.graph import Graph
from lineapy.data.types import Node


def are_nodes_equal(n1: Node, n2: Node, deep_check=False) -> bool:
    """
    - If deep_check is True, check each field of the nodes, otherwise, just check the ID.
    - deep_check is useful for testing
    """
    # first check if they are the same type
    if n1.id != n2.id:
        return False
    if deep_check:
        if n1.node_type != n2.node_type:
            return False
        # @dhruv TODO: then based on each node type do some custom testing
        # Maybe there is an easier way to just implement their __str__ and check that?
    return True


def are_graphs_identical(g1: Graph, g2: Graph, deep_check=False) -> bool:
    """
    This is simple util to traverse the graph for direct comparisons.
    In the future, for caching, we will have to do more advanced entity resolution
    """
    raise NotImplementedError

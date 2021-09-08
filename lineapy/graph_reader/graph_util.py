from typing import cast

import networkx as nx

from lineapy.data.graph import Graph
from lineapy.data.types import ArgumentNode, CallNode, Node, NodeType
from lineapy.utils import internal_warning_log


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


def are_nodes_content_equal(n1: Node, n2: Node) -> bool:
    """
    TODO:
    - we should probably make use of PyDantic's built in comparison, not possible right now since we have the extra ID field.
    - this test is not complete yet
    """
    # this one skips the ID checking
    # will refactor based on the linea-spec-db branch
    if n1.node_type != n2.node_type:
        return False

    if n1.node_type is NodeType.CallNode:
        n1 = cast(CallNode, n1)
        n2 = cast(CallNode, n2)
        if (
            n1.lineno != n2.lineno
            or n1.end_lineno != n2.end_lineno
            or n1.col_offset != n2.col_offset
            or n1.end_col_offset != n2.end_col_offset
        ):
            internal_warning_log("Nodes have different locations")
            return False
        if n1.function_name != n2.function_name:
            internal_warning_log(
                "Nodes have different names", n1.function_name, n2.function_name
            )
            return False
        if n1.assigned_variable_name != n2.assigned_variable_name:
            return False
        return True
    if n1.node_type is NodeType.ArgumentNode:
        n1 = cast(ArgumentNode, n1)
        n2 = cast(ArgumentNode, n2)
        if n1.positional_order != n2.positional_order:
            internal_warning_log(
                "Nodes have different positional_order",
                n1.positional_order,
                n2.positional_order,
            )
            return False
        if n1.value_node_id != n2.value_node_id:
            internal_warning_log(
                "Nodes have different value_node_id", n1.value_node_id, n2.value_node_id
            )
            return False
        if n2.value_literal != n2.value_literal:
            internal_warning_log(
                "Nodes have different value_literal", n1.value_literal, n2.value_literal
            )
            return False
        return True

    raise NotImplementedError("check other nodes")


def are_graphs_identical(g1: Graph, g2: Graph, deep_check=False) -> bool:
    """
    This is simple util to traverse the graph for direct comparisons.
    In the future, for caching, we will have to do more advanced entity resolution
    """
    return nx.is_isomorphic(g1.nx_graph, g2.nx_graph)

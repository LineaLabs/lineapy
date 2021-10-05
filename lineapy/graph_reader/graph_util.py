from typing import Iterator, cast, List, Dict, Optional, Any

from lineapy.data.types import (
    ArgumentNode,
    CallNode,
    FunctionDefinitionNode,
    Node,
    NodeType,
    DirectedEdge,
    SideEffectsNode,
    SourceLocation,
    StateChangeNode,
    StateDependencyType,
    VariableNode,
    LineaID,
)
from lineapy.utils import CaseNotHandledError, internal_warning_log

MAX_ARG_POSITION = 1000


def sort_node_by_position(nodes: List[Node]) -> List[LineaID]:
    """
    First checks for the line number, then the column. If
    """

    def get_key(n: Node):
        return (
            n.lineno if n.lineno else 0,
            n.col_offset if n.col_offset else 0,
        )

    nodes.sort(key=get_key, reverse=True)
    return [n.id for n in nodes]


def get_edges_from_nodes(nodes: List[Node]) -> Iterator[DirectedEdge]:
    for node in nodes:
        for id in get_parents_from_node(node):
            yield DirectedEdge(source_node_id=id, sink_node_id=node.id)


def get_arg_position(x: ArgumentNode):
    if x.positional_order is not None:
        return x.positional_order
    else:
        return MAX_ARG_POSITION


def get_parents_from_node(node: Node) -> Iterator[LineaID]:

    if node.node_type is NodeType.CallNode:
        node = cast(CallNode, node)
        yield from node.arguments
        yield node.function_id
    elif node.node_type is NodeType.ArgumentNode:
        node = cast(ArgumentNode, node)
        if node.value_node_id is not None:
            yield node.value_node_id
    elif node.node_type in [
        NodeType.LoopNode,
        NodeType.ConditionNode,
        NodeType.FunctionDefinitionNode,
    ]:
        node = cast(SideEffectsNode, node)
        if node.import_nodes is not None:
            yield from node.import_nodes
        if node.input_state_change_nodes is not None:
            yield from node.input_state_change_nodes
    elif node.node_type is NodeType.StateChangeNode:
        node = cast(StateChangeNode, node)
        if node.state_dependency_type is StateDependencyType.Write:
            yield node.associated_node_id
        elif node.state_dependency_type is StateDependencyType.Read:
            yield node.initial_value_node_id
    elif node.node_type is NodeType.VariableNode:
        node = cast(VariableNode, node)
        yield node.source_node_id


def get_segment_from_source_location(source_location: SourceLocation) -> str:
    code = source_location.source_code.code
    if source_location.lineno is source_location.end_lineno:
        return code.split("\n")[source_location.lineno - 1][
            source_location.col_offset : source_location.end_col_offset
        ]
    else:
        lines = code.split("\n")[
            source_location.lineno - 1 : source_location.end_lineno
        ]
        lines[0] = lines[0][source_location.col_offset :]
        lines[-1] = lines[-1][: source_location.end_col_offset]
        return "\n".join(lines)


def are_nodes_equal(n1: Node, n2: Node, deep_check=False) -> bool:
    """
    - If deep_check is True, check each field of the nodes, otherwise,
      just check the ID.
    - deep_check is useful for testing
    """
    # first check if they are the same type
    if n1.id != n2.id:
        return False
    if deep_check:
        if n1.node_type != n2.node_type:
            return False
        # TODO: then based on each node type do some custom testing
        # Maybe there is an easier way to just implement their __str__
        #   and check that?
    return True

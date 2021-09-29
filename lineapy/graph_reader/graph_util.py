from typing import Iterator, cast, List, Dict, Optional, Any

from lineapy.data.types import (
    ArgumentNode,
    CallNode,
    FunctionDefinitionNode,
    Node,
    NodeType,
    DirectedEdge,
    SideEffectsNode,
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

    nodes.sort(key=get_key)
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


def get_segment_from_code(code: str, node: Node) -> str:
    if node.lineno is node.end_lineno:
        return code.split("\n")[node.lineno - 1][
            node.col_offset : node.end_col_offset
        ]
    else:
        lines = code.split("\n")[node.lineno - 1 : node.end_lineno]
        lines[0] = lines[0][node.col_offset :]
        lines[-1] = lines[-1][: node.end_col_offset]
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


def are_nodes_content_equal(n1: Node, n2: Node, session_code: str) -> bool:
    """
    TODO:
    - we should add the syntax for comparison maybe?
    - we should probably make use of PyDantic's built in comparison,
      not possible right now since we have the extra ID field.
    - this test is not complete yet
    """
    # this one skips the ID checking
    # will refactor based on the linea-spec-db branch
    if n1.node_type != n2.node_type:
        return False

    if n1.node_type is NodeType.CallNode:
        n1 = cast(CallNode, n1)
        n2 = cast(CallNode, n2)

        if get_segment_from_code(session_code, n1) != get_segment_from_code(
            session_code, n2
        ):
            internal_warning_log("Nodes point to different code")
            return False
        if n1.function_name != n2.function_name:
            internal_warning_log(
                "Nodes have different names",
                n1.function_name,
                n2.function_name,
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
                "Nodes have different value_node_id",
                n1.value_node_id,
                n2.value_node_id,
            )
            return False
        if n2.value_literal != n2.value_literal:
            internal_warning_log(
                "Nodes have different value_literal",
                n1.value_literal,
                n2.value_literal,
            )
            return False
        return True
    if n1.node_type is NodeType.FunctionDefinitionNode:
        n1 = cast(FunctionDefinitionNode, n1)
        n2 = cast(FunctionDefinitionNode, n2)
        if n1.function_name != n2.function_name:
            internal_warning_log(
                "FunctionDefinitionNode different",
                n1.function_name,
                n2.function_name,
            )
            return False
        # TODO: add state variable checks!!!
        return True

    raise CaseNotHandledError(f"{n1.node_type} is not supported")

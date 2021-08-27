from lineapy.data.graph import Graph, DirectedEdge
from lineapy.data.types import (
    VariableAliasNode,
    ArgumentNode,
    CallNode,
)
from tests.stub_data.simple_graph import session
from tests.util import get_new_id

"""
a = [1,2,3]
b = a
a.append(4)
s = sum(b)
"""

arg_1 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_literal=1,
)

arg_2 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_literal=2,
)

arg_3 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=2,
    value_literal=3,
)

a_assign = CallNode(
    id=get_new_id(),
    session_id=session.id,
    code="a = [1,2,3]",
    function_name="__build_list__",
    assigned_variable_name="a",
    arguments=[arg_1.id, arg_2.id, arg_3.id],
)

b_assign = VariableAliasNode(
    id=get_new_id(),
    session_id=session.id,
    code="b = a",
    source_variable_id=a_assign.id,
)

arg_4 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_literal=4,
)

a_append = CallNode(
    id=get_new_id(),
    session_id=session.id,
    code="a.append(4)",
    function_name="append",
    function_module=a_assign.id,
    arguments=[arg_4.id],
)

b_arg = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=b_assign.id,
)

b_sum = CallNode(
    id=get_new_id(),
    session_id=session.id,
    code="s = sum(b)",
    function_name="sum",
    assigned_variable_name="s",
    arguments=[b_arg.id],
)

e_a_to_b = DirectedEdge(source_node_id=a_assign.id, sink_node_id=b_assign.id)
e_a_to_append = DirectedEdge(source_node_id=a_assign.id, sink_node_id=a_append.id)
e_b_to_sum = DirectedEdge(source_node_id=b_assign.id, sink_node_id=b_sum.id)

graph_with_alias_by_reference = Graph(
    nodes=[arg_1, arg_2, arg_3, arg_4, b_arg, a_assign, b_assign, a_append, b_sum],
)

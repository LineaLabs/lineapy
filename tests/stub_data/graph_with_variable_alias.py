from lineapy.data.graph import Graph
from tests.util import get_new_id
from tests.stub_data.simple_graph import session
from lineapy.data.types import (
    LiteralAssignNode,
    VariableAliasNode,
    DirectedEdge,
    ArgumentNode,
    CallNode,
)

"""
```
a = 0
b = a
a = 2
```

TODO: in our slicing test, we should make sure that getting the slice for b returns.

```
a = 0
b = a
```
"""

a_assign = LiteralAssignNode(
    id=get_new_id(),
    session_id=session.uuid,
    code="a = 0",
    assigned_variable_name="a",
    value=0,
)

b_assign = LiteralAssignNode(
    id=get_new_id(),
    session_id=session.uuid,
    code="b = a",
    assigned_variable_name="b",
    value_node_id=a_assign.id,
)

# I don't think we need to link this to the previous one?
# @dorx can you think of a case when this would be?
a_mutate = LiteralAssignNode(
    id=get_new_id(),
    session_id=session.uuid,
    code="a = 2",
    assigned_variable_name="a",
    value=2,
)

e_1 = DirectedEdge(source_node_id=a_assign.id, sink_node_id=b_assign.id)
e_2 = DirectedEdge(source_node_id=a_assign.id, sink_node_id=a_mutate.id)

graph_with_alias_by_value = Graph(
    nodes=[a_assign, b_assign, a_mutate], edges=[e_1, e_2]
)


"""
a = [1,2,3]
b = a
a.append(4)
s = sum(b)
"""

arg_1 = ArgumentNode(
    id=get_new_id(),
    session_id=session.uuid,
    positional_order=0,
    value_literal=1,
)

arg_2 = ArgumentNode(
    id=get_new_id(),
    session_id=session.uuid,
    positional_order=1,
    value_literal=2,
)

arg_3 = ArgumentNode(
    id=get_new_id(),
    session_id=session.uuid,
    positional_order=2,
    value_literal=3,
)

a_assign = CallNode(
    id=get_new_id(),
    session_id=session.uuid,
    code="a = [1,2,3]",
    function_name="__build_list__",
    assigned_variable_name="a",
    arguments=[arg_1, arg_2, arg_3],
)

b_assign = VariableAliasNode(
    id=get_new_id(),
    session_id=session.uuid,
    code="b = a",
    source_variable_id=a_assign.id,
)

arg_4 = ArgumentNode(
    id=get_new_id(),
    session_id=session.uuid,
    positional_order=0,
    value_literal=4,
)

a_append = CallNode(
    id=get_new_id(),
    session_id=session.uuid,
    code="a.append(4)",
    function_name="append",
    function_module=a_assign.id,
    arguments=[arg_4],
)

b_arg = ArgumentNode(
    id=get_new_id(),
    session_id=session.uuid,
    positional_order=0,
    value_node_id=b_assign.id,
)

b_sum = CallNode(
    id=get_new_id(),
    session_id=session.uuid,
    code="s = sum(b)",
    function_name="sum",
    assigned_variable_name="s",
    arguments=[b_arg],
)

e_a_to_b = DirectedEdge(source_node_id=a_assign.id, sink_node_id=b_assign.id)
e_a_to_append = DirectedEdge(source_node_id=a_assign.id, sink_node_id=a_append.id)
e_b_to_sum = DirectedEdge(source_node_id=b_assign.id, sink_node_id=b_sum.id)

graph_with_alias_by_reference = Graph(
    nodes=[a_assign, b_assign, a_append, b_sum],
    edges=[e_a_to_b, e_a_to_append, e_b_to_sum],
)

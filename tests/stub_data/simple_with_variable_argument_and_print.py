from lineapy.data.graph import Graph
from util import get_new_id
from lineapy.data.types import ArgumentNode, CallNode, DirectedEdge

from simple_graph import line_1, line_1_id, session, arg_literal

"""
```
a = abs(-1)
b = min(a, 10)
print(b)
```
"""

arg_a_id = get_new_id()

arg_a = ArgumentNode(id=arg_a_id, positional_order=1, value_call_id=line_1_id)

arg_10 = ArgumentNode(id=arg_a_id, positional_order=2, value_literal=10)

line_2_id = get_new_id()
line_2 = CallNode(
    id=line_2_id,
    session_id=session,
    function_name="min",
    assigned_variable_name="b",
    arguments=[],
)

e2 = DirectedEdge(source_node_id=line_1_id, sink_node_id=line_2_id)

simple_with_variable_argument_and_print = Graph(
    [line_1, arg_literal, arg_a, arg_10, line_2], [e2]
)

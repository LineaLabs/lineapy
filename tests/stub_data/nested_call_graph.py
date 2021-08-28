from lineapy.data.graph import Graph, DirectedEdge
from lineapy.data.types import (
    ArgumentNode,
    CallNode,
)
from tests.util import get_new_id, get_new_session

"""
```
a = min(abs(-11), 10)
```
"""

session = get_new_session()

arg_literal_id = get_new_id()

arg_literal = ArgumentNode(
    id=arg_literal_id, session_id=session.id, positional_order=1, value_literal=-11
)

line_1a_id = get_new_id()

line_1a = CallNode(
    id=line_1a_id,
    session_id=session.id,
    code="abs(-11)",
    function_name="abs",
    arguments=[arg_literal_id],
)

arg_1_id = get_new_id()

arg_10_id = get_new_id()

arg_1 = ArgumentNode(
    id=arg_1_id, session_id=session.id, positional_order=1, value_node_id=line_1a_id
)

arg_10 = ArgumentNode(
    id=arg_10_id, session_id=session.id, positional_order=2, value_literal=10
)

line_1b_id = get_new_id()
line_1b = CallNode(
    id=line_1b_id,
    session_id=session.id,
    code="min(abs(-11), 10)",
    function_name="min",
    assigned_variable_name="a",
    arguments=[arg_1_id, arg_10_id],
)

nested_call_graph = Graph([arg_literal, arg_1, arg_10, line_1a, line_1b])

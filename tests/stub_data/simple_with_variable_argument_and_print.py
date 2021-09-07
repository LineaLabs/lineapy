from lineapy.data.graph import Graph
from lineapy.data.types import ArgumentNode, CallNode
from tests.util import get_new_id, get_new_session

"""
```
a = abs(-11)
b = min(a, 10)
print(b)
```
"""

code = """a = abs(-11)
b = min(a, 10)
print(b)
"""

session = get_new_session(code)

arg_literal = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_literal=-11,
    lineno=1,
    col_offset=8,
    end_lineno=1,
    end_col_offset=11,
)

line_1 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    function_name="abs",
    assigned_variable_name="a",
    arguments=[arg_literal.id],
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=12,
)

arg_a_id = get_new_id()
arg_10_id = get_new_id()

arg_a = ArgumentNode(
    id=arg_a_id,
    session_id=session.id,
    positional_order=1,
    value_node_id=line_1.id,
    lineno=2,
    col_offset=8,
    end_lineno=2,
    end_col_offset=9,
)

arg_10 = ArgumentNode(
    id=arg_10_id,
    session_id=session.id,
    positional_order=2,
    value_literal=10,
    lineno=2,
    col_offset=11,
    end_lineno=2,
    end_col_offset=13,
)

line_2_id = get_new_id()
line_2 = CallNode(
    id=line_2_id,
    session_id=session.id,
    function_name="min",
    assigned_variable_name="b",
    arguments=[arg_a_id, arg_10_id],
    lineno=2,
    col_offset=0,
    end_lineno=2,
    end_col_offset=14,
)

arg_b_id = get_new_id()

arg_b = ArgumentNode(
    id=arg_b_id,
    session_id=session.id,
    positional_order=1,
    value_node_id=line_2_id,
    lineno=3,
    col_offset=6,
    end_lineno=3,
    end_col_offset=7,
)

line_3_id = get_new_id()
line_3 = CallNode(
    id=line_3_id,
    session_id=session.id,
    function_name="print",
    arguments=[arg_b_id],
    lineno=3,
    col_offset=0,
    end_lineno=3,
    end_col_offset=8,
)

simple_with_variable_argument_and_print = Graph(
    [arg_a, arg_10, arg_b, arg_literal, line_1, line_2, line_3]
)

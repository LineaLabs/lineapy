from lineapy.data.graph import Graph
from lineapy.data.types import (
    VariableNode,
    ArgumentNode,
    CallNode,
)
from tests.util import get_new_id, get_new_session

code = """a = [1,2,3]
b = a
a.append(4)
s = sum(b)
"""

session = get_new_session(code)

arg_1 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_literal=1,
    lineno=1,
    col_offset=5,
    end_lineno=1,
    end_col_offset=6,
)

arg_2 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_literal=2,
    lineno=1,
    col_offset=7,
    end_lineno=1,
    end_col_offset=8,
)

arg_3 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=2,
    value_literal=3,
    lineno=1,
    col_offset=9,
    end_lineno=1,
    end_col_offset=10,
)

a_assign = CallNode(
    id=get_new_id(),
    session_id=session.id,
    function_name="__build_list__",
    assigned_variable_name="a",
    arguments=[arg_1.id, arg_2.id, arg_3.id],
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=11,
)

b_assign = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_variable_id=a_assign.id,
    lineno=2,
    col_offset=0,
    end_lineno=2,
    end_col_offset=5,
)

arg_4 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_literal=4,
    lineno=3,
    col_offset=9,
    end_lineno=3,
    end_col_offset=10,
)

a_append = CallNode(
    id=get_new_id(),
    session_id=session.id,
    function_name="append",
    function_module=a_assign.id,
    arguments=[arg_4.id],
    lineno=3,
    col_offset=0,
    end_lineno=3,
    end_col_offset=11,
)

b_arg = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=b_assign.id,
    lineno=4,
    col_offset=8,
    end_lineno=4,
    end_col_offset=9,
)

b_sum = CallNode(
    id=get_new_id(),
    session_id=session.id,
    function_name="sum",
    assigned_variable_name="s",
    arguments=[b_arg.id],
    lineno=4,
    col_offset=0,
    end_lineno=4,
    end_col_offset=10,
)

graph_with_alias_by_reference = Graph(
    nodes=[
        arg_1,
        arg_2,
        arg_3,
        arg_4,
        b_arg,
        a_assign,
        b_assign,
        a_append,
        b_sum,
    ],
)

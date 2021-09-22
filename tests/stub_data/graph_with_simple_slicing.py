from lineapy.data.graph import Graph
from lineapy.data.types import (
    LiteralNode,
    Library,
    ImportNode,
    ArgumentNode,
    CallNode,
    VariableNode,
)
from tests.util import get_new_id, get_new_session

code = """a = 2
b = 2
c = min(b,5)
"""

sliced_code = """
b = 2
c = min(b,5)
"""

operator_lib = Library(id=get_new_id(), name="operator", version="1", path="")

session = get_new_session(code, libraries=[operator_lib])

# NOTE THAT ALL THE line numbers are off, waiting for saul

a_assign = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    assigned_variable_name="a",
    value=2,
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=5,
)

operator_module = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    library=operator_lib,
)

b_argument_node = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=2,
    value_literal=2,
    lineno=2,
    col_offset=0,
    end_lineno=2,
    end_col_offset=5,
)

literal_arg_node = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=2,
    value_literal=5,
)

c_assign = CallNode(
    id=get_new_id(),
    session_id=session.id,
    function_name="min",
    function_module=operator_module.id,  # built in
    assigned_variable_name="c",
    arguments=[b_argument_node.id, literal_arg_node.id],
    lineno=3,
    col_offset=0,
    end_lineno=3,
    end_col_offset=12,
)

graph_with_simple_slicing = Graph(
    [
        a_assign,
        operator_module,
        b_argument_node,
        literal_arg_node,
        c_assign,
    ],
    session,
)

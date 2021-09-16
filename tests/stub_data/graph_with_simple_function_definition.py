from click import argument
from lineapy.data.graph import Graph
from lineapy.data.types import (
    CallNode,
    FunctionDefinitionNode,
)
from tests.util import get_new_id, get_new_session


code = """def foo():
    return 1
a=foo()
"""
session = get_new_session(code)

definition_node = FunctionDefinitionNode(
    id=get_new_id(),
    session_id=session.id,
    function_name="foo",
    lineno=1,
    col_offset=0,
    end_lineno=2,
    end_col_offset=12,
)

assignment_node = CallNode(
    id=get_new_id(),
    session_id=session.id,
    function_name="foo",
    assigned_variable_name="a",
    locally_defined_function_id=definition_node.id,
    arguments=[],
    lineno=3,
    col_offset=0,
    end_lineno=3,
    end_col_offset=8,
)

simple_function_definition_graph = Graph([definition_node, assignment_node])

from click import argument
from lineapy.data.graph import Graph
from lineapy.data.types import (
    ArgumentNode,
    CallNode,
    FunctionDefinitionNode,
)
from tests.util import get_new_id, get_new_session


code = """def foo(a, b):
    return a - b
c = foo(b=1, a=2)
"""
session = get_new_session(code)

definition_node = FunctionDefinitionNode(
    id=get_new_id(),
    session_id=session.id,
    function_name="foo",
    lineno=1,
    col_offset=0,
    end_lineno=2,
    end_col_offset=16,
)


a_arg = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    keyword="a",
    value_literal=2,
    lineno=3,
    col_offset=8,
    end_lineno=9,
    end_col_offset=11,
)

b_arg = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    keyword="b",
    value_literal=1,
    lineno=3,
    col_offset=14,
    end_lineno=3,
    end_col_offset=16,
)


assignment_node = CallNode(
    id=get_new_id(),
    session_id=session.id,
    function_name="foo",
    assigned_variable_name="c",
    locally_defined_function_id=definition_node.id,
    arguments=[b_arg.id, a_arg.id],
    lineno=3,
    col_offset=0,
    end_lineno=3,
    end_col_offset=17,
)

simple_function_definition_graph = Graph(
    [definition_node, a_arg, b_arg, assignment_node], session
)

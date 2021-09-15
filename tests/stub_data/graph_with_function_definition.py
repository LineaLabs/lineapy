from lineapy.data.graph import Graph
from lineapy.data.types import (
    ImportNode,
    CallNode,
    Library,
    LiteralNode,
    FunctionDefinitionNode,
    StateChangeNode,
    StateDependencyType,
)
from tests.util import get_new_id, get_new_session

"""
This also doubles to test scope of the variable, as well as functions with mutation

"""

code = """import math
a = 0
def my_function():
    global a
    a = math.factorial(5)
my_function()
"""

math_lib = Library(id=get_new_id(), name="math", version="1", path="home")

session = get_new_session(code, libraries=[math_lib])

line_1_id = get_new_id()

line_1_import = ImportNode(
    id=line_1_id,
    session_id=session.id,
    library=math_lib,
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=11,
)

a_id = get_new_id()

line_2 = LiteralNode(
    id=a_id,
    session_id=session.id,
    assigned_variable_name="a",
    value=0,
    lineno=2,
    col_offset=0,
    end_lineno=2,
    end_col_offset=5,
)

fun_id = get_new_id()

a_input_state_change_id = get_new_id()
a_input_state_change = StateChangeNode(
    id=a_input_state_change_id,
    session_id=session.id,
    variable_name="a",
    associated_node_id=fun_id,
    initial_value_node_id=a_id,
    state_dependency_type=StateDependencyType.Read,
)

a_output_state_change_id = get_new_id()
a_output_state_change = StateChangeNode(
    id=a_output_state_change_id,
    session_id=session.id,
    variable_name="a",
    associated_node_id=fun_id,
    initial_value_node_id=a_id,
    state_dependency_type=StateDependencyType.Write,
)

fun_def_node = FunctionDefinitionNode(
    id=fun_id,
    session_id=session.id,
    function_name="my_function",
    input_state_change_nodes=[a_input_state_change_id],
    output_state_change_nodes=[a_output_state_change_id],
    import_nodes=[line_1_id],
    lineno=3,
    col_offset=0,
    end_lineno=5,
    end_col_offset=25,
)

func_call_id = get_new_id()
my_function_call = CallNode(
    id=func_call_id,
    session_id=session.id,
    function_name="my_function",
    locally_defined_function_id=fun_id,
    arguments=[],
    lineno=6,
    col_offset=0,
    end_lineno=6,
    end_col_offset=13,
)

graph_with_function_definition = Graph(
    [
        my_function_call,
        fun_def_node,
        line_1_import,
        line_2,
        a_input_state_change,
        a_output_state_change,
    ],
)

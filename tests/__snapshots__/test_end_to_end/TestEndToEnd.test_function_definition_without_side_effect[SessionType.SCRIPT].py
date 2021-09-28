import datetime
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    file_name="[source file path]",
    code="def foo(a, b):\n    return a - b\nc = foo(b=1, a=2)\n",
    working_directory="dummy_linea_repo/",
    session_name=None,
    user_name=None,
    hardware_spec=None,
    libraries=[],
)
function_definition_1 = FunctionDefinitionNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=0,
    end_lineno=2,
    end_col_offset=16,
    output_state_change_nodes=[],
    input_state_change_nodes=[],
    import_nodes=[],
    function_name="foo",
    value=None,
)
literal_1 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=3,
    col_offset=10,
    end_lineno=3,
    end_col_offset=11,
    value=1,
)
literal_2 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=3,
    col_offset=15,
    end_lineno=3,
    end_col_offset=16,
    value=2,
)
argument_1 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    keyword="b",
    positional_order=None,
    value_node_id=literal_1.id,
    value_literal=None,
)
argument_2 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    keyword="a",
    positional_order=None,
    value_node_id=literal_2.id,
    value_literal=None,
)
call_1 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=3,
    col_offset=0,
    end_lineno=3,
    end_col_offset=17,
    arguments=[argument_1.id, argument_2.id],
    function_name="foo",
    function_module=None,
    locally_defined_function_id=function_definition_1.id,
    assigned_variable_name="c",
    value=None,
)

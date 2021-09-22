from lineapy.data.types import *
from lineapy.utils import get_new_id

session_id = get_new_id()
function_definition_1 = FunctionDefinitionNode(
    id=get_new_id(),
    session_id=session_id,
    lineno=2,
    col_offset=0,
    end_lineno=3,
    end_col_offset=16,
    output_state_change_nodes=[],
    input_state_change_nodes=[],
    import_nodes=[],
    function_name="foo",
    value=None,
)
argument_1 = ArgumentNode(
    id=get_new_id(),
    session_id=session_id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    keyword="b",
    positional_order=None,
    value_node_id=None,
    value_literal=1,
)
argument_2 = ArgumentNode(
    id=get_new_id(),
    session_id=session_id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    keyword="a",
    positional_order=None,
    value_node_id=None,
    value_literal=2,
)
call_1 = CallNode(
    id=get_new_id(),
    session_id=session_id,
    lineno=4,
    col_offset=0,
    end_lineno=4,
    end_col_offset=17,
    arguments=[argument_1.id, argument_2.id],
    function_name="foo",
    function_module=None,
    locally_defined_function_id=function_definition_1.id,
    assigned_variable_name="c",
    value=None,
)

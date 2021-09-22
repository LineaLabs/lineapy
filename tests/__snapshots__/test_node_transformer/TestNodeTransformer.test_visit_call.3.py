from lineapy.data.types import *
from lineapy.utils import get_new_id

session_id = get_new_id()
argument_1 = ArgumentNode(
    id=get_new_id(),
    session_id=session_id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    keyword=None,
    positional_order=0,
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
    keyword=None,
    positional_order=1,
    value_node_id=None,
    value_literal=2,
)
call_1 = CallNode(
    id=get_new_id(),
    session_id=session_id,
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=9,
    arguments=[argument_1.id, argument_2.id],
    function_name="foo",
    function_module=None,
    locally_defined_function_id=None,
    assigned_variable_name=None,
    value=None,
)

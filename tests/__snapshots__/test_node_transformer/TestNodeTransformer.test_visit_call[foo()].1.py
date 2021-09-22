from lineapy.data.types import *
from lineapy.utils import get_new_id

session_id = get_new_id()
call_1 = CallNode(
    id=get_new_id(),
    session_id=session_id,
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=5,
    arguments=[],
    function_name="foo",
    function_module=None,
    locally_defined_function_id=None,
    assigned_variable_name=None,
    value=None,
)

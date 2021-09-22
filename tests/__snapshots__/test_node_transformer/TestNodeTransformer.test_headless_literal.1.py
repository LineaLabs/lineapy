from lineapy.data.types import *
from lineapy.utils import get_new_id

session_id = get_new_id()
literal_1 = LiteralNode(
    id=get_new_id(),
    session_id=session_id,
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=1,
    value=1,
    assigned_variable_name=None,
)

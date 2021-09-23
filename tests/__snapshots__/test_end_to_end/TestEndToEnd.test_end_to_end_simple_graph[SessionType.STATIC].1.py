import datetime
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.STATIC,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    file_name="[source file path]",
    code="import lineapy\na = abs(-11)\nlineapy.linea_publish(a, 'testing artifact publish')\n",
    session_name=None,
    user_name=None,
    hardware_spec=None,
    libraries=[
        Library(
            id=get_new_id(),
            name="lineapy",
            version=None,
            path=None,
        ),
    ],
)
import_1 = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=14,
    library=Library(
        id=get_new_id(),
        name="lineapy",
        version=None,
        path=None,
    ),
    attributes=None,
    alias=None,
    module=None,
)
argument_1 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    keyword=None,
    positional_order=0,
    value_node_id=None,
    value_literal=-11,
)
call_1 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=2,
    col_offset=0,
    end_lineno=2,
    end_col_offset=12,
    arguments=[argument_1.id],
    function_name="abs",
    function_module=None,
    locally_defined_function_id=None,
    assigned_variable_name="a",
    value=None,
)

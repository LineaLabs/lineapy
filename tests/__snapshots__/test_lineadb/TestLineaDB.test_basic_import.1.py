import datetime
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    file_name="[source file path]",
    code="from math import pow as power, sqrt as root\na = power(5, 2)\nb = root(a)",
    session_name=None,
    user_name=None,
    hardware_spec=None,
    libraries=[
        Library(
            id=get_new_id(),
            name="math",
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
    end_col_offset=43,
    library=Library(
        id=get_new_id(),
        name="math",
        version=None,
        path=None,
    ),
    attributes={"power": "pow", "root": "sqrt"},
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
    value_literal=5,
)
argument_2 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
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
    session_id=session.id,
    lineno=2,
    col_offset=0,
    end_lineno=2,
    end_col_offset=15,
    arguments=[argument_1.id, argument_2.id],
    function_name="power",
    function_module=import_1.id,
    locally_defined_function_id=None,
    assigned_variable_name="a",
    value=None,
)
argument_3 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    keyword=None,
    positional_order=0,
    value_node_id=call_1.id,
    value_literal=None,
)
call_2 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=3,
    col_offset=0,
    end_lineno=3,
    end_col_offset=11,
    arguments=[argument_3.id],
    function_name="root",
    function_module=import_1.id,
    locally_defined_function_id=None,
    assigned_variable_name="b",
    value=None,
)

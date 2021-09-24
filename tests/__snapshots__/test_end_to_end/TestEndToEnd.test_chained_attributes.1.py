import datetime
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    file_name="[source file path]",
    code="import altair; altair.data_transformers.enable('json')",
    working_directory="dummy_linea_repo/",
    session_name=None,
    user_name=None,
    hardware_spec=None,
    libraries=[
        Library(
            id=get_new_id(),
            name="altair",
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
    end_col_offset=13,
    library=Library(
        id=get_new_id(),
        name="altair",
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
    positional_order=1,
    value_node_id=None,
    value_literal="data_transformers",
)
argument_2 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
    keyword=None,
    positional_order=0,
    value_node_id=None,
    value_literal="json",
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
    value_node_id=import_1.id,
    value_literal=None,
)
call_1 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=15,
    end_lineno=1,
    end_col_offset=39,
    arguments=[argument_1.id, argument_3.id],
    function_name="getattr",
    function_module=None,
    locally_defined_function_id=None,
    assigned_variable_name=None,
    value=None,
)
call_2 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=15,
    end_lineno=1,
    end_col_offset=54,
    arguments=[argument_2.id],
    function_name="enable",
    function_module=call_1.id,
    locally_defined_function_id=None,
    assigned_variable_name=None,
    value=None,
)

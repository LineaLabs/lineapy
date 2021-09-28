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
    libraries=[
        Library(
            id=get_new_id(),
            name="altair",
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
    ),
)
literal_1 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=47,
    end_lineno=1,
    end_col_offset=53,
    value="json",
)
lookup_1 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="getattr",
)
lookup_2 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="getattr",
)
literal_2 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    value="data_transformers",
)
literal_3 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    value="enable",
)
argument_1 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=import_1.id,
)
argument_2 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=literal_1.id,
)
argument_3 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=literal_2.id,
)
argument_4 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=literal_3.id,
)
call_1 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=15,
    end_lineno=1,
    end_col_offset=39,
    arguments=[argument_1.id, argument_3.id],
    function_id=lookup_2.id,
)
argument_5 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=call_1.id,
)
call_2 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=15,
    end_lineno=1,
    end_col_offset=46,
    arguments=[argument_4.id, argument_5.id],
    function_id=lookup_1.id,
)
call_3 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=15,
    end_lineno=1,
    end_col_offset=54,
    arguments=[argument_2.id],
    function_id=call_2.id,
)

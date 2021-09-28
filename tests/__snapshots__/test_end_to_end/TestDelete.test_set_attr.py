import datetime
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    file_name="[source file path]",
    code="import types; x = types.SimpleNamespace(); x.hi = 1",
    working_directory="dummy_linea_repo/",
    libraries=[
        Library(
            id=get_new_id(),
            name="types",
        ),
    ],
)
import_1 = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=12,
    library=Library(
        id=get_new_id(),
        name="types",
    ),
)
lookup_1 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="getattr",
)
literal_1 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    value="SimpleNamespace",
)
lookup_2 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="setattr",
)
literal_2 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    value="hi",
)
literal_3 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=50,
    end_lineno=1,
    end_col_offset=51,
    value=1,
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
    positional_order=1,
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
    positional_order=2,
    value_node_id=literal_3.id,
)
call_1 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=18,
    end_lineno=1,
    end_col_offset=39,
    arguments=[argument_1.id, argument_2.id],
    function_id=lookup_1.id,
)
call_2 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=14,
    end_lineno=1,
    end_col_offset=41,
    arguments=[],
    function_id=call_1.id,
)
variable_1 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=call_2.id,
    assigned_variable_name="x",
)
argument_5 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=variable_1.id,
)
call_3 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=43,
    end_lineno=1,
    end_col_offset=51,
    arguments=[argument_3.id, argument_4.id, argument_5.id],
    function_id=lookup_2.id,
)

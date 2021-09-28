import datetime
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    file_name="[source file path]",
    code="b = 1 < 2 < 3\nassert b",
    working_directory="dummy_linea_repo/",
    libraries=[],
)
literal_1 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=4,
    end_lineno=1,
    end_col_offset=5,
    value=1,
)
literal_2 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=8,
    end_lineno=1,
    end_col_offset=9,
    value=2,
)
lookup_1 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="lt",
)
literal_3 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=12,
    end_lineno=1,
    end_col_offset=13,
    value=3,
)
lookup_2 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="lt",
)
argument_1 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=literal_1.id,
)
argument_2 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=literal_2.id,
)
argument_3 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=literal_3.id,
)
call_1 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=4,
    end_lineno=1,
    end_col_offset=13,
    arguments=[argument_1.id, argument_2.id],
    function_id=lookup_1.id,
)
argument_4 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=call_1.id,
)
call_2 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=13,
    arguments=[argument_3.id, argument_4.id],
    function_id=lookup_2.id,
)
variable_1 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=call_2.id,
    assigned_variable_name="b",
)

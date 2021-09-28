import datetime
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    file_name="[source file path]",
    code="a = abs(11)\nb = min(a, 10)\nprint(b)\n",
    working_directory="dummy_linea_repo/",
    libraries=[],
)
literal_1 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=8,
    end_lineno=1,
    end_col_offset=10,
    value=11,
)
lookup_1 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="abs",
)
literal_2 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=2,
    col_offset=11,
    end_lineno=2,
    end_col_offset=13,
    value=10,
)
lookup_2 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="min",
)
lookup_3 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="print",
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
call_1 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=11,
    arguments=[argument_1.id],
    function_id=lookup_1.id,
)
variable_1 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=call_1.id,
    assigned_variable_name="a",
)
argument_3 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=variable_1.id,
)
call_2 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=2,
    col_offset=0,
    end_lineno=2,
    end_col_offset=14,
    arguments=[argument_2.id, argument_3.id],
    function_id=lookup_2.id,
)
variable_2 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=call_2.id,
    assigned_variable_name="b",
)
argument_4 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=variable_2.id,
)
call_3 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=3,
    col_offset=0,
    end_lineno=3,
    end_col_offset=8,
    arguments=[argument_4.id],
    function_id=lookup_3.id,
)

import datetime
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    file_name="[source file path]",
    code="ls = [1,2]\nassert ls[0] == 1",
    working_directory="dummy_linea_repo/",
    libraries=[],
)
literal_1 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=6,
    end_lineno=1,
    end_col_offset=7,
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
    name="__build_list__",
)
literal_3 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=2,
    col_offset=10,
    end_lineno=2,
    end_col_offset=11,
    value=0,
)
lookup_2 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="getitem",
)
literal_4 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=2,
    col_offset=16,
    end_lineno=2,
    end_col_offset=17,
    value=1,
)
lookup_3 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="eq",
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
argument_4 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=literal_4.id,
)
call_1 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=10,
    arguments=[argument_1.id, argument_2.id],
    function_id=lookup_1.id,
)
variable_1 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=call_1.id,
    assigned_variable_name="ls",
)
argument_5 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=variable_1.id,
)
call_2 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=2,
    col_offset=7,
    end_lineno=2,
    end_col_offset=12,
    arguments=[argument_3.id, argument_5.id],
    function_id=lookup_2.id,
)
argument_6 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=call_2.id,
)
call_3 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=2,
    col_offset=7,
    end_lineno=2,
    end_col_offset=17,
    arguments=[argument_4.id, argument_6.id],
    function_id=lookup_3.id,
)

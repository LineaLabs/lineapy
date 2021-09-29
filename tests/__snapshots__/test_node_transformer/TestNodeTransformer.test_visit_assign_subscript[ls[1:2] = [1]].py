import datetime
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    file_name="[source file path]",
    code="ls=[1,2,3]\na=1\nb=4\nls[1:2] = [1]",
    working_directory="dummy_linea_repo/",
    libraries=[],
)
lookup_1 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="__build_list__",
)
lookup_2 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="setitem",
)
lookup_3 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="slice",
)
lookup_4 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="__build_list__",
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
    col_offset=6,
    end_lineno=1,
    end_col_offset=7,
    value=2,
)
literal_3 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=8,
    end_lineno=1,
    end_col_offset=9,
    value=3,
)
literal_4 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=2,
    col_offset=0,
    end_lineno=2,
    end_col_offset=3,
    value=1,
)
literal_5 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=3,
    col_offset=0,
    end_lineno=3,
    end_col_offset=3,
    value=4,
)
literal_6 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=4,
    col_offset=3,
    end_lineno=4,
    end_col_offset=4,
    value=1,
)
literal_7 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=4,
    col_offset=5,
    end_lineno=4,
    end_col_offset=6,
    value=2,
)
literal_8 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=4,
    col_offset=11,
    end_lineno=4,
    end_col_offset=12,
    value=1,
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
    positional_order=2,
    value_node_id=literal_3.id,
)
variable_1 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=literal_4.id,
    assigned_variable_name="a",
)
variable_2 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=literal_5.id,
    assigned_variable_name="b",
)
argument_4 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=literal_6.id,
)
argument_5 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=literal_7.id,
)
argument_6 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=literal_8.id,
)
call_1 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=10,
    arguments=[argument_1.id, argument_2.id, argument_3.id],
    function_id=lookup_1.id,
)
call_2 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=4,
    col_offset=3,
    end_lineno=4,
    end_col_offset=6,
    arguments=[argument_4.id, argument_5.id],
    function_id=lookup_3.id,
)
call_3 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=4,
    col_offset=10,
    end_lineno=4,
    end_col_offset=13,
    arguments=[argument_6.id],
    function_id=lookup_4.id,
)
variable_3 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=call_1.id,
    assigned_variable_name="ls",
)
argument_7 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=call_2.id,
)
argument_8 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=2,
    value_node_id=call_3.id,
)
argument_9 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=variable_3.id,
)
call_4 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=4,
    col_offset=0,
    end_lineno=4,
    end_col_offset=13,
    arguments=[argument_7.id, argument_8.id, argument_9.id],
    function_id=lookup_2.id,
)

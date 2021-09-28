import datetime
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    file_name="[source file path]",
    code="import lineapy\na = 1\nb = a + 2\nc = 2\nd = 4\ne = d + a\nf = a * b * c\n10\ne\ng = e\n\nlineapy.linea_publish(f, 'f')\n",
    working_directory="dummy_linea_repo/",
    libraries=[
        Library(
            id=get_new_id(),
            name="lineapy",
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
    ),
)
literal_1 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=2,
    col_offset=0,
    end_lineno=2,
    end_col_offset=5,
    value=1,
)
literal_2 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=3,
    col_offset=8,
    end_lineno=3,
    end_col_offset=9,
    value=2,
)
lookup_1 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="add",
)
literal_3 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=4,
    col_offset=0,
    end_lineno=4,
    end_col_offset=5,
    value=2,
)
literal_4 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=5,
    col_offset=0,
    end_lineno=5,
    end_col_offset=5,
    value=4,
)
lookup_2 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="add",
)
lookup_3 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="mul",
)
lookup_4 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="mul",
)
literal_5 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=8,
    col_offset=0,
    end_lineno=8,
    end_col_offset=2,
    value=10,
)
variable_1 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=literal_1.id,
    assigned_variable_name="a",
)
argument_1 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=literal_2.id,
)
variable_2 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=literal_3.id,
    assigned_variable_name="c",
)
variable_3 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=literal_4.id,
    assigned_variable_name="d",
)
argument_2 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=variable_1.id,
)
argument_3 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=variable_1.id,
)
argument_4 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=variable_1.id,
)
argument_5 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=variable_2.id,
)
argument_6 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=variable_3.id,
)
call_1 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=3,
    col_offset=0,
    end_lineno=3,
    end_col_offset=9,
    arguments=[argument_1.id, argument_2.id],
    function_id=lookup_1.id,
)
call_2 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=6,
    col_offset=0,
    end_lineno=6,
    end_col_offset=9,
    arguments=[argument_3.id, argument_6.id],
    function_id=lookup_2.id,
)
variable_4 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=call_1.id,
    assigned_variable_name="b",
)
variable_5 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=10,
    col_offset=0,
    end_lineno=10,
    end_col_offset=5,
    source_node_id=call_2.id,
    assigned_variable_name="e",
)
argument_7 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=variable_4.id,
)
variable_6 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=variable_5.id,
    assigned_variable_name="g",
)
call_3 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=7,
    col_offset=4,
    end_lineno=7,
    end_col_offset=9,
    arguments=[argument_4.id, argument_7.id],
    function_id=lookup_3.id,
)
argument_8 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=call_3.id,
)
call_4 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=7,
    col_offset=0,
    end_lineno=7,
    end_col_offset=13,
    arguments=[argument_5.id, argument_8.id],
    function_id=lookup_4.id,
)
variable_7 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=call_4.id,
    assigned_variable_name="f",
)

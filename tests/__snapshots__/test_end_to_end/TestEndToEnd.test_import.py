import datetime
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    file_name="[source file path]",
    code="from math import pow as power, sqrt as root\na = power(5, 2)\nb = root(a)\n",
    working_directory="dummy_linea_repo/",
    libraries=[
        Library(
            id=get_new_id(),
            name="math",
        ),
    ],
)
lookup_1 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="getattr",
)
literal_1 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    value="pow",
)
lookup_2 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="getattr",
)
literal_2 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    value="sqrt",
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
    ),
    attributes={"power": "pow", "root": "sqrt"},
)
literal_3 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=2,
    col_offset=10,
    end_lineno=2,
    end_col_offset=11,
    value=5,
)
literal_4 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=2,
    col_offset=13,
    end_lineno=2,
    end_col_offset=14,
    value=2,
)
argument_1 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
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
    positional_order=0,
    value_node_id=import_1.id,
)
argument_4 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=import_1.id,
)
argument_5 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=literal_3.id,
)
argument_6 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=literal_4.id,
)
call_1 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    arguments=[argument_1.id, argument_3.id],
    function_id=lookup_1.id,
)
call_2 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    arguments=[argument_2.id, argument_4.id],
    function_id=lookup_2.id,
)
variable_1 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=call_1.id,
    assigned_variable_name="power",
)
variable_2 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=call_2.id,
    assigned_variable_name="root",
)
call_3 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=2,
    col_offset=0,
    end_lineno=2,
    end_col_offset=15,
    arguments=[argument_5.id, argument_6.id],
    function_id=variable_1.id,
)
variable_3 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=call_3.id,
    assigned_variable_name="a",
)
argument_7 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=variable_3.id,
)
call_4 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=3,
    col_offset=0,
    end_lineno=3,
    end_col_offset=11,
    arguments=[argument_7.id],
    function_id=variable_2.id,
)
variable_4 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=call_4.id,
    assigned_variable_name="b",
)

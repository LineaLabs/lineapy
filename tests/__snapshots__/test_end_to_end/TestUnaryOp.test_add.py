import datetime
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    file_name="[source file path]",
    code="from decimal import Decimal\nobj = Decimal('3.1415926535897932384626433832795028841971')\nassert +obj != obj",
    working_directory="dummy_linea_repo/",
    libraries=[
        Library(
            id=get_new_id(),
            name="decimal",
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
    value="Decimal",
)
lookup_2 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="pos",
)
lookup_3 = LookupNode(
    id=get_new_id(),
    session_id=session.id,
    name="ne",
)
import_1 = ImportNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=1,
    col_offset=0,
    end_lineno=1,
    end_col_offset=27,
    library=Library(
        id=get_new_id(),
        name="decimal",
    ),
    attributes={"Decimal": "Decimal"},
)
literal_2 = LiteralNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=2,
    col_offset=14,
    end_lineno=2,
    end_col_offset=58,
    value="3.1415926535897932384626433832795028841971",
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
    positional_order=0,
    value_node_id=import_1.id,
)
argument_3 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=literal_2.id,
)
call_1 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    arguments=[argument_1.id, argument_2.id],
    function_id=lookup_1.id,
)
variable_1 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=call_1.id,
    assigned_variable_name="Decimal",
)
call_2 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=2,
    col_offset=0,
    end_lineno=2,
    end_col_offset=59,
    arguments=[argument_3.id],
    function_id=variable_1.id,
)
variable_2 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=call_2.id,
    assigned_variable_name="obj",
)
argument_4 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=variable_2.id,
)
argument_5 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=1,
    value_node_id=variable_2.id,
)
call_3 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=3,
    col_offset=7,
    end_lineno=3,
    end_col_offset=11,
    arguments=[argument_4.id],
    function_id=lookup_2.id,
)
argument_6 = ArgumentNode(
    id=get_new_id(),
    session_id=session.id,
    positional_order=0,
    value_node_id=call_3.id,
)
call_4 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    lineno=3,
    col_offset=7,
    end_lineno=3,
    end_col_offset=18,
    arguments=[argument_5.id, argument_6.id],
    function_id=lookup_3.id,
)

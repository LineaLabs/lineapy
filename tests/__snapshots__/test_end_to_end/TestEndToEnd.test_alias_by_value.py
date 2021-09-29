import datetime
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    file_name="[source file path]",
    code="a = 0\nb = a\na = 2\n",
    working_directory="dummy_linea_repo/",
    libraries=[],
)
variable_2 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=VariableNode(
        id=get_new_id(),
        session_id=session.id,
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=5,
        source_node_id=LiteralNode(
            id=get_new_id(),
            session_id=session.id,
            lineno=1,
            col_offset=0,
            end_lineno=1,
            end_col_offset=5,
            value=0,
        ).id,
        assigned_variable_name="a",
    ).id,
    assigned_variable_name="b",
)
variable_3 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=LiteralNode(
        id=get_new_id(),
        session_id=session.id,
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=5,
        value=2,
    ).id,
    assigned_variable_name="a",
)

import datetime
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.STATIC,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    file_name="[source file path]",
    code="import lineapy\na = abs(11)\nlineapy.linea_publish(a, 'testing artifact publish')\n",
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
variable_1 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=CallNode(
        id=get_new_id(),
        session_id=session.id,
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=11,
        arguments=[
            ArgumentNode(
                id=get_new_id(),
                session_id=session.id,
                positional_order=0,
                value_node_id=LiteralNode(
                    id=get_new_id(),
                    session_id=session.id,
                    lineno=2,
                    col_offset=8,
                    end_lineno=2,
                    end_col_offset=10,
                    value=11,
                ).id,
            ).id
        ],
        function_id=LookupNode(
            id=get_new_id(),
            session_id=session.id,
            name="abs",
        ).id,
    ).id,
    assigned_variable_name="a",
)

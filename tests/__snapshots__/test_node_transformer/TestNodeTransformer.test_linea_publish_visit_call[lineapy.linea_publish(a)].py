import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    working_directory="dummy_linea_repo/",
    libraries=[],
)
source_1 = SourceCode(
    id=get_new_id(),
    code="""a=1
lineapy.linea_publish(a)""",
    location=PosixPath("[source file path]"),
)
variable_1 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=3,
        source_code=source_1.id,
    ),
    source_node_id=LiteralNode(
        id=get_new_id(),
        session_id=session.id,
        source_location=SourceLocation(
            lineno=1,
            col_offset=2,
            end_lineno=1,
            end_col_offset=3,
            source_code=source_1.id,
        ),
        value=1,
    ).id,
    assigned_variable_name="a",
)

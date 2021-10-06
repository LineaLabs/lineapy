import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.STATIC,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    working_directory="dummy_linea_repo/",
)
source_1 = SourceCode(
    id=get_new_id(),
    code="foo(b=1)",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    arguments=[
        ArgumentNode(
            id=get_new_id(),
            session_id=session.id,
            keyword="b",
            value_node_id=LiteralNode(
                id=get_new_id(),
                session_id=session.id,
                source_location=SourceLocation(
                    lineno=1,
                    col_offset=6,
                    end_lineno=1,
                    end_col_offset=7,
                    source_code=source_1.id,
                ),
                value=1,
            ).id,
        ).id
    ],
    function_id=LookupNode(
        id=get_new_id(),
        session_id=session.id,
        name="foo",
    ).id,
)

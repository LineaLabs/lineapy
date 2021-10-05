import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.STATIC,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    working_directory="dummy_linea_repo/",
    libraries=[],
)
source_1 = SourceCode(
    id=get_new_id(),
    code="get_ipython().system('')",
    location=PosixPath("[source file path]"),
)
call_3 = CallNode(
    id=get_new_id(),
    session_id=session.id,
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=24,
        source_code=source_1.id,
    ),
    arguments=[
        ArgumentNode(
            id=get_new_id(),
            session_id=session.id,
            positional_order=0,
            value_node_id=LiteralNode(
                id=get_new_id(),
                session_id=session.id,
                source_location=SourceLocation(
                    lineno=1,
                    col_offset=21,
                    end_lineno=1,
                    end_col_offset=23,
                    source_code=source_1.id,
                ),
                value="",
            ).id,
        ).id
    ],
    function_id=CallNode(
        id=get_new_id(),
        session_id=session.id,
        source_location=SourceLocation(
            lineno=1,
            col_offset=0,
            end_lineno=1,
            end_col_offset=20,
            source_code=source_1.id,
        ),
        arguments=[
            ArgumentNode(
                id=get_new_id(),
                session_id=session.id,
                positional_order=0,
                value_node_id=CallNode(
                    id=get_new_id(),
                    session_id=session.id,
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=0,
                        end_lineno=1,
                        end_col_offset=13,
                        source_code=source_1.id,
                    ),
                    arguments=[],
                    function_id=LookupNode(
                        id=get_new_id(),
                        session_id=session.id,
                        name="get_ipython",
                    ).id,
                ).id,
            ).id,
            ArgumentNode(
                id=get_new_id(),
                session_id=session.id,
                positional_order=1,
                value_node_id=LiteralNode(
                    id=get_new_id(),
                    session_id=session.id,
                    value="system",
                ).id,
            ).id,
        ],
        function_id=LookupNode(
            id=get_new_id(),
            session_id=session.id,
            name="getattr",
        ).id,
    ).id,
)

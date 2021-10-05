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
    code="a = '{{ {0} }}'.format('foo')",
    location=PosixPath("[source file path]"),
)
variable_1 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=29,
        source_code=source_1.id,
    ),
    source_node_id=CallNode(
        id=get_new_id(),
        session_id=session.id,
        source_location=SourceLocation(
            lineno=1,
            col_offset=4,
            end_lineno=1,
            end_col_offset=29,
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
                        col_offset=23,
                        end_lineno=1,
                        end_col_offset=28,
                        source_code=source_1.id,
                    ),
                    value="foo",
                ).id,
            ).id
        ],
        function_id=CallNode(
            id=get_new_id(),
            session_id=session.id,
            source_location=SourceLocation(
                lineno=1,
                col_offset=4,
                end_lineno=1,
                end_col_offset=22,
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
                            col_offset=4,
                            end_lineno=1,
                            end_col_offset=15,
                            source_code=source_1.id,
                        ),
                        value="{{ {0} }}",
                    ).id,
                ).id,
                ArgumentNode(
                    id=get_new_id(),
                    session_id=session.id,
                    positional_order=1,
                    value_node_id=LiteralNode(
                        id=get_new_id(),
                        session_id=session.id,
                        value="format",
                    ).id,
                ).id,
            ],
            function_id=LookupNode(
                id=get_new_id(),
                session_id=session.id,
                name="getattr",
            ).id,
        ).id,
    ).id,
    assigned_variable_name="a",
)

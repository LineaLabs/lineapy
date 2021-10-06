import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
<<<<<<< ours
=======
    file_name="[source file path]",
    code="a=1\nb=2\nc=3\na > b",
>>>>>>> theirs
    working_directory="dummy_linea_repo/",
)
source_1 = SourceCode(
    id=get_new_id(),
    code="""a=1
b=2
a > b""",
    location=PosixPath("[source file path]"),
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
        end_col_offset=3,
        value=3,
    ).id,
    assigned_variable_name="c",
)
call_1 = CallNode(
    id=get_new_id(),
    session_id=session.id,
<<<<<<< ours
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=5,
        source_code=source_1.id,
    ),
=======
    lineno=4,
    col_offset=0,
    end_lineno=4,
    end_col_offset=5,
>>>>>>> theirs
    arguments=[
        ArgumentNode(
            id=get_new_id(),
            session_id=session.id,
            positional_order=0,
            value_node_id=VariableNode(
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
            ).id,
        ).id,
        ArgumentNode(
            id=get_new_id(),
            session_id=session.id,
            positional_order=1,
            value_node_id=VariableNode(
                id=get_new_id(),
                session_id=session.id,
                source_location=SourceLocation(
                    lineno=2,
                    col_offset=0,
                    end_lineno=2,
                    end_col_offset=3,
                    source_code=source_1.id,
                ),
                source_node_id=LiteralNode(
                    id=get_new_id(),
                    session_id=session.id,
                    source_location=SourceLocation(
                        lineno=2,
                        col_offset=2,
                        end_lineno=2,
                        end_col_offset=3,
                        source_code=source_1.id,
                    ),
                    value=2,
                ).id,
                assigned_variable_name="b",
            ).id,
        ).id,
    ],
    function_id=LookupNode(
        id=get_new_id(),
        session_id=session.id,
        name="gt",
    ).id,
)

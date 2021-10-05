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
    code="""def foo(a, b):
    return a - b
c = foo(b=1, a=2)
""",
    location=PosixPath(
        "[source file path]"
    ),
)
variable_1 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    source_node_id=CallNode(
        id=get_new_id(),
        session_id=session.id,
        source_location=SourceLocation(
            lineno=3,
            col_offset=4,
            end_lineno=3,
            end_col_offset=17,
            source_code=source_1.id,
        ),
        arguments=[
            ArgumentNode(
                id=get_new_id(),
                session_id=session.id,
                keyword="a",
                value_node_id=LiteralNode(
                    id=get_new_id(),
                    session_id=session.id,
                    source_location=SourceLocation(
                        lineno=3,
                        col_offset=15,
                        end_lineno=3,
                        end_col_offset=16,
                        source_code=source_1.id,
                    ),
                    value=2,
                ).id,
            ).id,
            ArgumentNode(
                id=get_new_id(),
                session_id=session.id,
                keyword="b",
                value_node_id=LiteralNode(
                    id=get_new_id(),
                    session_id=session.id,
                    source_location=SourceLocation(
                        lineno=3,
                        col_offset=10,
                        end_lineno=3,
                        end_col_offset=11,
                        source_code=source_1.id,
                    ),
                    value=1,
                ).id,
            ).id,
        ],
        function_id=FunctionDefinitionNode(
            id=get_new_id(),
            session_id=session.id,
            source_location=SourceLocation(
                lineno=1,
                col_offset=0,
                end_lineno=2,
                end_col_offset=16,
                source_code=source_1.id,
            ),
            output_state_change_nodes=[],
            input_state_change_nodes=[],
            import_nodes=[],
            function_name="foo",
        ).id,
    ).id,
    assigned_variable_name="c",
)

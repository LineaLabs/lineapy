import datetime
from lineapy.data.types import *
from lineapy.utils import get_new_id

session = SessionContext(
    id=get_new_id(),
    environment_type=SessionType.SCRIPT,
    creation_time=datetime.datetime(1, 1, 1, 0, 0),
    file_name="[source file path]",
    code="a = '{{ {0} }}'.format('foo')",
    working_directory="dummy_linea_repo/",
    libraries=[],
)
variable_1 = VariableNode(
    id=get_new_id(),
    session_id=session.id,
    source_node_id=CallNode(
        id=get_new_id(),
        session_id=session.id,
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=29,
        arguments=[
            ArgumentNode(
                id=get_new_id(),
                session_id=session.id,
                positional_order=0,
                value_node_id=LiteralNode(
                    id=get_new_id(),
                    session_id=session.id,
                    lineno=1,
                    col_offset=23,
                    end_lineno=1,
                    end_col_offset=28,
                    value="foo",
                ).id,
            ).id
        ],
        function_id=CallNode(
            id=get_new_id(),
            session_id=session.id,
            lineno=1,
            col_offset=4,
            end_lineno=1,
            end_col_offset=22,
            arguments=[
                ArgumentNode(
                    id=get_new_id(),
                    session_id=session.id,
                    positional_order=0,
                    value_node_id=LiteralNode(
                        id=get_new_id(),
                        session_id=session.id,
                        lineno=1,
                        col_offset=4,
                        end_lineno=1,
                        end_col_offset=15,
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

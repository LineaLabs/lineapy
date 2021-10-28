import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""def foo(a, b):
    return a - b
c = foo(b=1, a=2)
d = foo(5,1)
""",
    location=PosixPath("[source file path]"),
)
global_1 = GlobalNode(
    name="foo",
    call_id=CallNode(
        source_location=SourceLocation(
            lineno=1,
            col_offset=0,
            end_lineno=2,
            end_col_offset=16,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="l_exec_statement",
        ).id,
        positional_args=[
            LiteralNode(
                value="""def foo(a, b):
    return a - b""",
            ).id
        ],
    ).id,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=17,
        source_code=source_1.id,
    ),
    function_id=global_1.id,
    keyword_args={
        "a": LiteralNode(
            source_location=SourceLocation(
                lineno=3,
                col_offset=15,
                end_lineno=3,
                end_col_offset=16,
                source_code=source_1.id,
            ),
            value=2,
        ).id,
        "b": LiteralNode(
            source_location=SourceLocation(
                lineno=3,
                col_offset=10,
                end_lineno=3,
                end_col_offset=11,
                source_code=source_1.id,
            ),
            value=1,
        ).id,
    },
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=4,
        end_lineno=4,
        end_col_offset=12,
        source_code=source_1.id,
    ),
    function_id=global_1.id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=8,
                end_lineno=4,
                end_col_offset=9,
                source_code=source_1.id,
            ),
            value=5,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=10,
                end_lineno=4,
                end_col_offset=11,
                source_code=source_1.id,
            ),
            value=1,
        ).id,
    ],
)

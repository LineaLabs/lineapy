import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
def foo(a):
    return a - b
b=10
c = foo(15)

lineapy.linea_publish(c, \'c\')
""",
    location=PosixPath("[source file path]"),
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=4,
        end_lineno=5,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        function_id=LookupNode(
            name="getitem",
        ).id,
        positional_args=[
            CallNode(
                source_location=SourceLocation(
                    lineno=2,
                    col_offset=0,
                    end_lineno=3,
                    end_col_offset=16,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="__exec__",
                ).id,
                positional_args=[
                    LiteralNode(
                        value="""def foo(a):
    return a - b""",
                    ).id,
                    LiteralNode(
                        value=False,
                    ).id,
                    LiteralNode(
                        value="foo",
                    ).id,
                ],
            ).id,
            LiteralNode(
                value=0,
            ).id,
        ],
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=5,
                col_offset=8,
                end_lineno=5,
                end_col_offset=10,
                source_code=source_1.id,
            ),
            value=15,
        ).id
    ],
    global_reads={
        "b": LiteralNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=2,
                end_lineno=4,
                end_col_offset=4,
                source_code=source_1.id,
            ),
            value=10,
        ).id
    },
)

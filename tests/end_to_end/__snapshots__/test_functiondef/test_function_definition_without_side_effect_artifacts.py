import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
b=30
def foo(a):
    return a - 10
c = foo(b)

lineapy.save(c, \'c\')
""",
    location=PosixPath("[source file path]"),
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=4,
        end_lineno=5,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        function_id=LookupNode(
            name="getitem",
        ).id,
        positional_args=[
            CallNode(
                source_location=SourceLocation(
                    lineno=3,
                    col_offset=0,
                    end_lineno=4,
                    end_col_offset=17,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="__exec__",
                ).id,
                positional_args=[
                    LiteralNode(
                        value="""def foo(a):
    return a - 10""",
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
                lineno=2,
                col_offset=2,
                end_lineno=2,
                end_col_offset=4,
                source_code=source_1.id,
            ),
            value=30,
        ).id
    ],
)

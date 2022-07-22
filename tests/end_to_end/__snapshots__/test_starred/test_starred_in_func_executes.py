import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""def func(*args):
    return [m for m in args]

name = "myname"
x = func(*name)
""",
    location=PosixPath("[source file path]"),
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=4,
        end_lineno=5,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    function_id=GlobalNode(
        name="func",
        call_id=CallNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=0,
                end_lineno=2,
                end_col_offset=28,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="l_exec_statement",
            ).id,
            positional_args=[
                LiteralNode(
                    value="""def func(*args):
    return [m for m in args]""",
                ).id
            ],
        ).id,
    ).id,
    positional_args=[
        *LiteralNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=7,
                end_lineno=4,
                end_col_offset=15,
                source_code=source_1.id,
            ),
            value="myname",
        ).id
    ],
)

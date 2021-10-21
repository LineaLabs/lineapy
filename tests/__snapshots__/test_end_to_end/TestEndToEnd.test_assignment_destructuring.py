import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="a, b = (1, 2)",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=7,
        end_lineno=1,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="__build_tuple__",
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=8,
                end_lineno=1,
                end_col_offset=9,
                source_code=source_1.id,
            ),
            value=1,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=11,
                end_lineno=1,
                end_col_offset=12,
                source_code=source_1.id,
            ),
            value=2,
        ).id,
    ],
    global_reads={},
)
call_2 = CallNode(
    function_id=LookupNode(
        name="getitem",
    ).id,
    positional_args=[
        call_1.id,
        LiteralNode(
            value=0,
        ).id,
    ],
    global_reads={},
)
call_3 = CallNode(
    function_id=LookupNode(
        name="getitem",
    ).id,
    positional_args=[
        call_1.id,
        LiteralNode(
            value=1,
        ).id,
    ],
    global_reads={},
)

import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""
z = 10
z = (x := 8)
""",
    location=PosixPath("[source file path]"),
)
literal_1 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    value=10,
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=5,
        end_lineno=3,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_alias",
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=3,
                col_offset=10,
                end_lineno=3,
                end_col_offset=11,
                source_code=source_1.id,
            ),
            value=8,
        ).id
    ],
)

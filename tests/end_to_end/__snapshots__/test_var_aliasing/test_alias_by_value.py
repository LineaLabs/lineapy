import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""a = 0
b = a
a = 2
""",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_alias",
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=4,
                end_lineno=1,
                end_col_offset=5,
                source_code=source_1.id,
            ),
            value=0,
        ).id
    ],
)
literal_2 = LiteralNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    value=2,
)

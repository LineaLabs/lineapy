import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="a = abs(11)",
    location=PosixPath("[source file path]"),
)
lookup_1 = LookupNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    name="abs",
)
literal_1 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=8,
        end_lineno=1,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    value=11,
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_1.id],
)

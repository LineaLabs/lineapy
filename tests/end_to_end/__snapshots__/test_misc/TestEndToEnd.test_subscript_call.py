import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="l_list",
)
lookup_2 = LookupNode(
    name="getitem",
)
source_1 = SourceCode(
    code="[0][abs(0)]",
    location=PosixPath("[source file path]"),
)
literal_1 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=1,
        end_lineno=1,
        end_col_offset=2,
        source_code=source_1.id,
    ),
    value=0,
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=3,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_1.id],
)
lookup_3 = LookupNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    name="abs",
)
literal_2 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=8,
        end_lineno=1,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    value=0,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[literal_2.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_1.id, call_2.id],
)

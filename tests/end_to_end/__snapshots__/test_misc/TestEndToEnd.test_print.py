import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""a = abs(11)
b = min(a, 10)
print(b)
""",
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
lookup_2 = LookupNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    name="min",
)
literal_2 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=11,
        end_lineno=2,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    value=10,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[call_1.id, literal_2.id],
)
lookup_3 = LookupNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    name="print",
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_2.id],
)

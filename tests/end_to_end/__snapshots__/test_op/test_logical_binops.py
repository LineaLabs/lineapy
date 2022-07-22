import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="eq",
)
lookup_2 = LookupNode(
    name="le",
)
lookup_3 = LookupNode(
    name="gt",
)
lookup_4 = LookupNode(
    name="ne",
)
lookup_5 = LookupNode(
    name="lt",
)
lookup_6 = LookupNode(
    name="ge",
)
source_1 = SourceCode(
    code="""a = 1
b = 2
r1 = a == b
r2 = a != b
r3 = a < b
r4 = a <= b
r5 = a > b
r6 = a >= b
""",
    location=PosixPath("[source file path]"),
)
literal_1 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    value=1,
)
literal_2 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    value=2,
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=5,
        end_lineno=3,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_1.id, literal_2.id],
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=5,
        end_lineno=4,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[literal_1.id, literal_2.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=5,
        end_lineno=5,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[literal_1.id, literal_2.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=5,
        end_lineno=6,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_1.id, literal_2.id],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=5,
        end_lineno=7,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[literal_1.id, literal_2.id],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=5,
        end_lineno=8,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
    positional_args=[literal_1.id, literal_2.id],
)

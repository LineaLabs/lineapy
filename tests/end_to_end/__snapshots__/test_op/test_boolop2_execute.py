import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

lookup_1 = LookupNode(
    name="gt",
)
lookup_2 = LookupNode(
    name="lt",
)
lookup_3 = LookupNode(
    name="and_",
)
lookup_4 = LookupNode(
    name="or_",
)
lookup_5 = LookupNode(
    name="lt",
)
lookup_6 = LookupNode(
    name="gt",
)
source_1 = SourceCode(
    code="""x = 1>2
y = 1<2
z = x and y
q = (1>2 or 1<2)
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
        lineno=1,
        col_offset=6,
        end_lineno=1,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    value=2,
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    function_id=lookup_1.id,
    positional_args=[literal_1.id, literal_2.id],
)
literal_3 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    value=1,
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=6,
        end_lineno=2,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    value=2,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=7,
        source_code=source_1.id,
    ),
    function_id=lookup_2.id,
    positional_args=[literal_3.id, literal_4.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=lookup_3.id,
    positional_args=[call_1.id, call_2.id],
)
literal_5 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=5,
        end_lineno=4,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    value=1,
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=7,
        end_lineno=4,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    value=2,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=5,
        end_lineno=4,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    function_id=lookup_6.id,
    positional_args=[literal_5.id, literal_6.id],
)
literal_7 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=12,
        end_lineno=4,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    value=1,
)
literal_8 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=14,
        end_lineno=4,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    value=2,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=12,
        end_lineno=4,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    function_id=lookup_5.id,
    positional_args=[literal_7.id, literal_8.id],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=5,
        end_lineno=4,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    function_id=lookup_4.id,
    positional_args=[call_4.id, call_5.id],
)

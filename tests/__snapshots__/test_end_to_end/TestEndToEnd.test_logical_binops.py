import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

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
    function_id=LookupNode(
        name="eq",
    ).id,
    positional_args=[literal_1.id, literal_2.id],
    global_reads={},
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=5,
        end_lineno=4,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="ne",
    ).id,
    positional_args=[literal_1.id, literal_2.id],
    global_reads={},
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=5,
        end_lineno=5,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="lt",
    ).id,
    positional_args=[literal_1.id, literal_2.id],
    global_reads={},
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=5,
        end_lineno=6,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="le",
    ).id,
    positional_args=[literal_1.id, literal_2.id],
    global_reads={},
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=5,
        end_lineno=7,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="gt",
    ).id,
    positional_args=[literal_1.id, literal_2.id],
    global_reads={},
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=5,
        end_lineno=8,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="ge",
    ).id,
    positional_args=[literal_1.id, literal_2.id],
    global_reads={},
)

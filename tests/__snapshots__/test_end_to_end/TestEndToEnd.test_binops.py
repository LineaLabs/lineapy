import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""a = 11
b = 2

r1 = a + b
r2 = a - b
r3 =a * b
r4 =a / b
r5 =a // b
r6 =a % b
r7 =a ** b
r8 =a << b
r9 =a >> b
r10 =a | b
r11 =a ^ b
r12 =a & b
""",
    location=PosixPath("[source file path]"),
)
literal_1 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    value=11,
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
        lineno=4,
        col_offset=5,
        end_lineno=4,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="add",
    ).id,
    positional_args=[literal_1.id, literal_2.id],
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=5,
        end_lineno=5,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="sub",
    ).id,
    positional_args=[literal_1.id, literal_2.id],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=4,
        end_lineno=6,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="mul",
    ).id,
    positional_args=[literal_1.id, literal_2.id],
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=4,
        end_lineno=7,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="truediv",
    ).id,
    positional_args=[literal_1.id, literal_2.id],
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=4,
        end_lineno=8,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="floordiv",
    ).id,
    positional_args=[literal_1.id, literal_2.id],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=9,
        col_offset=4,
        end_lineno=9,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="mod",
    ).id,
    positional_args=[literal_1.id, literal_2.id],
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=10,
        col_offset=4,
        end_lineno=10,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="pow",
    ).id,
    positional_args=[literal_1.id, literal_2.id],
)
call_8 = CallNode(
    source_location=SourceLocation(
        lineno=11,
        col_offset=4,
        end_lineno=11,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="lshift",
    ).id,
    positional_args=[literal_1.id, literal_2.id],
)
call_9 = CallNode(
    source_location=SourceLocation(
        lineno=12,
        col_offset=4,
        end_lineno=12,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="rshift",
    ).id,
    positional_args=[literal_1.id, literal_2.id],
)
call_10 = CallNode(
    source_location=SourceLocation(
        lineno=13,
        col_offset=5,
        end_lineno=13,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="or_",
    ).id,
    positional_args=[literal_1.id, literal_2.id],
)
call_11 = CallNode(
    source_location=SourceLocation(
        lineno=14,
        col_offset=5,
        end_lineno=14,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="xor",
    ).id,
    positional_args=[literal_1.id, literal_2.id],
)
call_12 = CallNode(
    source_location=SourceLocation(
        lineno=15,
        col_offset=5,
        end_lineno=15,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="and_",
    ).id,
    positional_args=[literal_1.id, literal_2.id],
)

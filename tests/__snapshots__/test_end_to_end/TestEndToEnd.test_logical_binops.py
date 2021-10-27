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
)
global_1 = GlobalNode(
    name="foo",
    call_id=call_1.id,
)
global_2 = GlobalNode(
    name="c",
    call_id=call_1.id,
)
global_3 = GlobalNode(
    name="v",
    call_id=call_1.id,
)
global_4 = GlobalNode(
    name="df",
    call_id=call_1.id,
)
global_5 = GlobalNode(
    name="r10",
    call_id=call_1.id,
)
global_6 = GlobalNode(
    name="r9",
    call_id=call_1.id,
)
global_7 = GlobalNode(
    name="r7",
    call_id=call_1.id,
)
global_8 = GlobalNode(
    name="r8",
    call_id=call_1.id,
)
global_9 = GlobalNode(
    name="r6",
    call_id=call_1.id,
)
global_10 = GlobalNode(
    name="r5",
    call_id=call_1.id,
)
global_11 = GlobalNode(
    name="r4",
    call_id=call_1.id,
)
global_12 = GlobalNode(
    name="pandas",
    call_id=call_1.id,
)
global_13 = GlobalNode(
    name="DataFrame",
    call_id=call_1.id,
)
global_14 = GlobalNode(
    name="r2",
    call_id=call_1.id,
)
global_15 = GlobalNode(
    name="r1",
    call_id=call_1.id,
)
global_16 = GlobalNode(
    name="img",
    call_id=call_1.id,
)
global_17 = GlobalNode(
    name="r3",
    call_id=call_1.id,
)
global_18 = GlobalNode(
    name="PIL.Image",
    call_id=call_1.id,
)
global_19 = GlobalNode(
    name="pd",
    call_id=call_1.id,
)
global_20 = GlobalNode(
    name="r11",
    call_id=call_1.id,
)
global_21 = GlobalNode(
    name="math",
    call_id=call_1.id,
)
global_22 = GlobalNode(
    name="x",
    call_id=call_1.id,
)
global_23 = GlobalNode(
    name="bs",
    call_id=call_1.id,
)
global_24 = GlobalNode(
    name="open",
    call_id=call_1.id,
)
global_25 = GlobalNode(
    name="my_function",
    call_id=call_1.id,
)
global_26 = GlobalNode(
    name="plt",
    call_id=call_1.id,
)
global_27 = GlobalNode(
    name="new_df",
    call_id=call_1.id,
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
)

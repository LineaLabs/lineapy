import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""a = abs(11)
b = min(a, 10)
print(b)
""",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="abs",
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=8,
                end_lineno=1,
                end_col_offset=10,
                source_code=source_1.id,
            ),
            value=11,
        ).id
    ],
)
global_1 = GlobalNode(
    name="foo",
    call_id=call_1.id,
)
global_2 = GlobalNode(
    name="math",
    call_id=call_1.id,
)
global_3 = GlobalNode(
    name="a",
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
    name="ls",
    call_id=call_1.id,
)
global_7 = GlobalNode(
    name="r9",
    call_id=call_1.id,
)
global_8 = GlobalNode(
    name="v",
    call_id=call_1.id,
)
global_9 = GlobalNode(
    name="r7",
    call_id=call_1.id,
)
global_10 = GlobalNode(
    name="r8",
    call_id=call_1.id,
)
global_11 = GlobalNode(
    name="r6",
    call_id=call_1.id,
)
global_12 = GlobalNode(
    name="r5",
    call_id=call_1.id,
)
global_13 = GlobalNode(
    name="r4",
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
    name="pandas",
    call_id=call_1.id,
)
global_18 = GlobalNode(
    name="DataFrame",
    call_id=call_1.id,
)
global_19 = GlobalNode(
    name="PIL.Image",
    call_id=call_1.id,
)
global_20 = GlobalNode(
    name="plt",
    call_id=call_1.id,
)
global_21 = GlobalNode(
    name="pd",
    call_id=call_1.id,
)
global_22 = GlobalNode(
    name="r11",
    call_id=call_1.id,
)
global_23 = GlobalNode(
    name="r3",
    call_id=call_1.id,
)
global_24 = GlobalNode(
    name="c",
    call_id=call_1.id,
)
global_25 = GlobalNode(
    name="x",
    call_id=call_1.id,
)
global_26 = GlobalNode(
    name="open",
    call_id=call_1.id,
)
global_27 = GlobalNode(
    name="bs",
    call_id=call_1.id,
)
global_28 = GlobalNode(
    name="b",
    call_id=call_1.id,
)
global_29 = GlobalNode(
    name="new_df",
    call_id=call_1.id,
)
global_30 = GlobalNode(
    name="my_function",
    call_id=call_1.id,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="print",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=4,
                end_lineno=2,
                end_col_offset=14,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="min",
            ).id,
            positional_args=[
                call_1.id,
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=2,
                        col_offset=11,
                        end_lineno=2,
                        end_col_offset=13,
                        source_code=source_1.id,
                    ),
                    value=10,
                ).id,
            ],
        ).id
    ],
)

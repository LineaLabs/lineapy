import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""a = [1,2,3]
b = a
a.append(4)
c = 2
r1 = c in a
r2 = c not in a
s = sum(b)
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
        name="l_list",
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=5,
                end_lineno=1,
                end_col_offset=6,
                source_code=source_1.id,
            ),
            value=1,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=7,
                end_lineno=1,
                end_col_offset=8,
                source_code=source_1.id,
            ),
            value=2,
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=9,
                end_lineno=1,
                end_col_offset=10,
                source_code=source_1.id,
            ),
            value=3,
        ).id,
    ],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=3,
            col_offset=0,
            end_lineno=3,
            end_col_offset=8,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            call_1.id,
            LiteralNode(
                value="append",
            ).id,
        ],
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=3,
                col_offset=9,
                end_lineno=3,
                end_col_offset=10,
                source_code=source_1.id,
            ),
            value=4,
        ).id
    ],
)
mutate_1 = MutateNode(
    source_id=GlobalNode(
        name="c",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_2 = MutateNode(
    source_id=GlobalNode(
        name="DataFrame",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_3 = MutateNode(
    source_id=GlobalNode(
        name="math",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_4 = MutateNode(
    source_id=GlobalNode(
        name="r5",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_5 = MutateNode(
    source_id=GlobalNode(
        name="df",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_6 = MutateNode(
    source_id=GlobalNode(
        name="r1",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_7 = MutateNode(
    source_id=GlobalNode(
        name="x",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_8 = MutateNode(
    source_id=GlobalNode(
        name="r6",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_9 = MutateNode(
    source_id=GlobalNode(
        name="r8",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_10 = MutateNode(
    source_id=GlobalNode(
        name="new_df",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_11 = MutateNode(
    source_id=GlobalNode(
        name="r10",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_12 = MutateNode(
    source_id=GlobalNode(
        name="v",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_13 = MutateNode(
    source_id=GlobalNode(
        name="bs",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_14 = MutateNode(
    source_id=GlobalNode(
        name="altair",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_15 = MutateNode(
    source_id=GlobalNode(
        name="pandas",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_16 = MutateNode(
    source_id=GlobalNode(
        name="a",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_17 = MutateNode(
    source_id=GlobalNode(
        name="foo",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_18 = MutateNode(
    source_id=GlobalNode(
        name="img",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_19 = MutateNode(
    source_id=GlobalNode(
        name="r9",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_20 = MutateNode(
    source_id=GlobalNode(
        name="plt",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_21 = MutateNode(
    source_id=call_1.id,
    call_id=call_3.id,
)
mutate_22 = MutateNode(
    source_id=GlobalNode(
        name="b",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_23 = MutateNode(
    source_id=GlobalNode(
        name="r7",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_24 = MutateNode(
    source_id=GlobalNode(
        name="pd",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_25 = MutateNode(
    source_id=GlobalNode(
        name="r2",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_26 = MutateNode(
    source_id=GlobalNode(
        name="ls",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_27 = MutateNode(
    source_id=GlobalNode(
        name="r4",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_28 = MutateNode(
    source_id=GlobalNode(
        name="PIL.Image",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_29 = MutateNode(
    source_id=GlobalNode(
        name="my_function",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_30 = MutateNode(
    source_id=GlobalNode(
        name="r3",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_31 = MutateNode(
    source_id=GlobalNode(
        name="open",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
mutate_32 = MutateNode(
    source_id=GlobalNode(
        name="r11",
        call_id=call_1.id,
    ).id,
    call_id=call_3.id,
)
literal_6 = LiteralNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=4,
        end_lineno=4,
        end_col_offset=5,
        source_code=source_1.id,
    ),
    value=2,
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=5,
        col_offset=5,
        end_lineno=5,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="contains",
    ).id,
    positional_args=[mutate_21.id, literal_6.id],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=6,
        col_offset=5,
        end_lineno=6,
        end_col_offset=15,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="not_",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=6,
                col_offset=5,
                end_lineno=6,
                end_col_offset=15,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="contains",
            ).id,
            positional_args=[mutate_21.id, literal_6.id],
        ).id
    ],
)
call_7 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=4,
        end_lineno=7,
        end_col_offset=10,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="sum",
    ).id,
    positional_args=[mutate_21.id],
)

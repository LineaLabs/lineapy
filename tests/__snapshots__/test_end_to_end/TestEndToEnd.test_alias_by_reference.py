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
mutate_1 = MutateNode(
    source_id=call_1.id,
    call_id=CallNode(
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
    ).id,
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
    positional_args=[mutate_1.id, literal_6.id],
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
            positional_args=[mutate_1.id, literal_6.id],
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
        source_location=SourceLocation(
            lineno=7,
            col_offset=4,
            end_lineno=7,
            end_col_offset=7,
            source_code=source_1.id,
        ),
        name="sum",
    ).id,
    positional_args=[mutate_1.id],
)

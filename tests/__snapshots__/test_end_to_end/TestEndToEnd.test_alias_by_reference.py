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
        name="__build_list__",
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
    global_reads={},
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
        global_reads={},
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
    global_reads={},
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
    positional_args=[call_1.id, literal_6.id],
    global_reads={},
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
            positional_args=[call_1.id, literal_6.id],
            global_reads={},
        ).id
    ],
    global_reads={},
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
    positional_args=[call_1.id],
    global_reads={},
)

import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
a = []
b = 0
for x in range(9):
    a.append(x)
    b+=x
x = sum(a)
y = x + b
lineapy.linea_publish(y, \'y\')
""",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=4,
        end_lineno=2,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="__build_list__",
    ).id,
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=4,
        col_offset=0,
        end_lineno=6,
        end_col_offset=8,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="__exec__",
    ).id,
    positional_args=[
        LiteralNode(
            value="""for x in range(9):
    a.append(x)
    b+=x""",
        ).id,
        LiteralNode(
            value=False,
        ).id,
        LiteralNode(
            value="b",
        ).id,
        LiteralNode(
            value="x",
        ).id,
    ],
    keyword_args={
        "a": call_1.id,
        "b": LiteralNode(
            source_location=SourceLocation(
                lineno=3,
                col_offset=4,
                end_lineno=3,
                end_col_offset=5,
                source_code=source_1.id,
            ),
            value=0,
        ).id,
        "range": LookupNode(
            name="range",
        ).id,
    },
)
call_4 = CallNode(
    function_id=LookupNode(
        name="getitem",
    ).id,
    positional_args=[
        call_2.id,
        LiteralNode(
            value=1,
        ).id,
    ],
)
call_6 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=4,
        end_lineno=8,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="add",
    ).id,
    positional_args=[
        CallNode(
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
        ).id,
        CallNode(
            function_id=LookupNode(
                name="getitem",
            ).id,
            positional_args=[
                call_2.id,
                LiteralNode(
                    value=0,
                ).id,
            ],
        ).id,
    ],
)

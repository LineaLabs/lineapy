import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="x = [i + 1 for i in range(3)]",
    location=PosixPath("[source file path]"),
)
call_2 = CallNode(
    function_id=LookupNode(
        name="getitem",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=4,
                end_lineno=1,
                end_col_offset=29,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="__exec__",
            ).id,
            positional_args=[
                LiteralNode(
                    value="[i + 1 for i in range(3)]",
                ).id,
                LiteralNode(
                    value=1,
                ).id,
            ],
            keyword_args={
                "range": LookupNode(
                    name="range",
                ).id
            },
        ).id,
        LiteralNode(
            value=0,
        ).id,
    ],
    keyword_args={},
)

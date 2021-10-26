import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""a = 10
b = lambda x: x + a
c = b(10)
""",
    location=PosixPath("[source file path]"),
)
literal_4 = LiteralNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=6,
        source_code=source_1.id,
    ),
    value=10,
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=4,
        end_lineno=3,
        end_col_offset=9,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        function_id=LookupNode(
            name="getitem",
        ).id,
        positional_args=[
            CallNode(
                source_location=SourceLocation(
                    lineno=2,
                    col_offset=4,
                    end_lineno=2,
                    end_col_offset=19,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="__exec__",
                ).id,
                positional_args=[
                    LiteralNode(
                        value="lambda x: x + a",
                    ).id,
                    LiteralNode(
                        value=True,
                    ).id,
                ],
            ).id,
            LiteralNode(
                value=0,
            ).id,
        ],
    ).id,
    positional_args=[
        LiteralNode(
            source_location=SourceLocation(
                lineno=3,
                col_offset=6,
                end_lineno=3,
                end_col_offset=8,
                source_code=source_1.id,
            ),
            value=10,
        ).id
    ],
)

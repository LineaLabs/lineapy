import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils import get_new_id

source_1 = SourceCode(
    code="""a = 1
b=a.imag == 1""",
    location=PosixPath("[source file path]"),
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=2,
        end_lineno=2,
        end_col_offset=13,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="eq",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=2,
                end_lineno=2,
                end_col_offset=8,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="getattr",
            ).id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=4,
                        end_lineno=1,
                        end_col_offset=5,
                        source_code=source_1.id,
                    ),
                    value=1,
                ).id,
                LiteralNode(
                    value="imag",
                ).id,
            ],
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=2,
                col_offset=12,
                end_lineno=2,
                end_col_offset=13,
                source_code=source_1.id,
            ),
            value=1,
        ).id,
    ],
)

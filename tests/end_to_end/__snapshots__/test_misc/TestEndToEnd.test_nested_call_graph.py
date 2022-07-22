import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="a = min(abs(11), 10)",
    location=PosixPath("[source file path]"),
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=4,
        end_lineno=1,
        end_col_offset=20,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        source_location=SourceLocation(
            lineno=1,
            col_offset=4,
            end_lineno=1,
            end_col_offset=7,
            source_code=source_1.id,
        ),
        name="min",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=8,
                end_lineno=1,
                end_col_offset=15,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                source_location=SourceLocation(
                    lineno=1,
                    col_offset=8,
                    end_lineno=1,
                    end_col_offset=11,
                    source_code=source_1.id,
                ),
                name="abs",
            ).id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=12,
                        end_lineno=1,
                        end_col_offset=14,
                        source_code=source_1.id,
                    ),
                    value=11,
                ).id
            ],
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=17,
                end_lineno=1,
                end_col_offset=19,
                source_code=source_1.id,
            ),
            value=10,
        ).id,
    ],
)

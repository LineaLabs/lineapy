import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="[0][abs(0)]",
    location=PosixPath("[source file path]"),
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=11,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="getitem",
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=0,
                end_lineno=1,
                end_col_offset=3,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="l_list",
            ).id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=1,
                        end_lineno=1,
                        end_col_offset=2,
                        source_code=source_1.id,
                    ),
                    value=0,
                ).id
            ],
        ).id,
        CallNode(
            source_location=SourceLocation(
                lineno=1,
                col_offset=4,
                end_lineno=1,
                end_col_offset=10,
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
                name="abs",
            ).id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=1,
                        col_offset=8,
                        end_lineno=1,
                        end_col_offset=9,
                        source_code=source_1.id,
                    ),
                    value=0,
                ).id
            ],
        ).id,
    ],
)
